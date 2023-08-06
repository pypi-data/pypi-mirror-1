##############################################################################
#
# Copyright 2009 Lovely Systems AG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
##############################################################################

from StringIO import StringIO
from pickle import dumps, loads
import bz2
from google.appengine.api import memcache, datastore
from google.appengine.api.datastore import Entity
from google.appengine.api.datastore_types import ResolveAppId
from google.appengine.datastore import datastore_pb
from google.appengine.ext import db

from lovely.gae.async import defer
from lovely.gae.batch import create_markers
from lovely.gae.db.property import PickleProperty


def local_key(k):
    appid = ResolveAppId(None)
    if isinstance(k, Entity):
        if appid == k.key().app():
            return
        local_key(k.key())
        local_key(k.values())
    if isinstance(k, db.Key):
        if appid == k.app():
            return
        k._Key__reference.set_app(appid)
        return
    elif isinstance(k, dict):
        map(local_key, k.items())
    elif isinstance(k, list) or isinstance(k, tuple):
        map(local_key, k)

class BatchCallback(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, mc_key):
        Snapshot.finished_markers(mc_key, *self.args, **self.kwargs)

class Snapshot(db.Model):

    STATUS_STARTED=1
    STATUS_STORING=2
    STATUS_FINISHED=3
    STATUS_ERROR=4
    m_time = db.DateTimeProperty(auto_now_add=True, auto_now=True,
                                 required=True)
    c_time = db.DateTimeProperty(auto_now_add=True, required=True)
    status = db.IntegerProperty(choices=(STATUS_STARTED,
                                     STATUS_STORING,
                                     STATUS_FINISHED,
                                     STATUS_ERROR), required=True)
    kinds = db.StringListProperty(indexed=False)
    markers = PickleProperty(default={})
    finished_kinds = db.StringListProperty(indexed=False)

    @classmethod
    def create(cls, kinds):
        s = cls(kinds=kinds, status=Snapshot.STATUS_STARTED)
        s.put()
        for kind in kinds:
            create_markers(
                kind, batchsize=200,
                callback=BatchCallback(s.key(), kind))
        return s

    def restore(self):
        if self.status != self.STATUS_FINISHED:
            raise RuntimeError, "Snapshot not finished %s" % self.key()
        q = RangeBackup.all(keys_only=True).filter('snapshot', self)
        for range_key in q:
            defer(restore_rangebackup, [range_key])

    def delete(self):
        keys = RangeBackup.all(keys_only=True).filter('snapshot', self).fetch(1000)
        while True:
            tk = keys[:10]
            del keys[:10]
            if tk:
                db.delete(tk)
            else:
                break
        return super(Snapshot, self).delete()

    @classmethod
    def finished_markers(cls, mc_key, key, kind):
        """called for any markers for kind"""
        self = cls.get(key)
        res = memcache.get(mc_key)
        if res is None:
            self.status = cls.STATUS_ERROR
            self.put()
            return
        self.markers[kind] = res
        self.status = cls.STATUS_STORING
        self.put()
        # create a job for each marker
        res = [None] +  res + [None]
        memcache.set('unfinished_markers:%s:%s' % (kind, self.key()), len(res)-1)
        for pos, m in enumerate(res):
            if pos<len(res)-1:
                defer(create_rangebackup, [self.key(), kind, pos, m, res[pos+1]],
                      once_only=False)

    def finished_store(self, kind):
        self.finished_kinds.append(kind)
        # check if we have all
        for k in self.kinds:
            if k not in self.finished_kinds:
                self.put()
                return
        self.status = self.STATUS_FINISHED
        self.put()

def create_rangebackup(snapshot, kind, pos, start, end):
    return RangeBackup.create(snapshot, kind, pos,
                              start and str(start) or None,
                              end and str(end) or None)

def restore_rangebackup(k):
    rb = RangeBackup.get(k)
    rb.restore()

class RangeBackup(db.Model):

    start = db.StringProperty()
    end = db.StringProperty()
    kind_ = db.StringProperty(required=True)

    keys = db.StringListProperty()
    entities = db.BlobProperty()
    snapshot = db.ReferenceProperty(Snapshot, required=True)

    @classmethod
    def create(cls, s_key, kind, pos, start, end):
        q = datastore.Query(kind)
        if start:
            q['__key__ >'] = db.Key(start)
        if end:
            q['__key__ <='] = db.Key(end)
        q.Order('__key__')
        entities = tuple(q.Get(1000))
        pbs = []
        s = 0
        req = datastore_pb.PutRequest()
        req.entity_list().extend([e._ToPb() for e in entities])
        v = dumps(req.Encode(), -1)
        v = bz2.compress(v)
        size=len(v)
        key_name = 'RB:%s:%s:%010d:%s' % (s_key.id_or_name(), kind, pos, size)
        rb = cls(key_name=key_name,
                 entities=v,
                 start=start,
                 end=end,
                 kind_=kind,
                 snapshot=s_key,
                 keys = [str(e.key()) for e in entities])
        rb.put()
        unfinished_markers = memcache.decr(
            'unfinished_markers:%s:%s' % (kind, s_key))
        if unfinished_markers<=0:
            # this is the last range to be done
            rb.snapshot.finished_store(rb.kind_)

    def iter_entities(self):
        req = datastore_pb.PutRequest()
        v = loads(bz2.decompress(self.entities))
        req.MergeFromString(v)
        for epb in req.entity_list():
            yield Entity._FromPb(epb)

    def restore(self):
        existing_query = datastore.Query(self.kind_, keys_only=True)
        if self.start:
            existing_query['__key__ >'] = db.Key(self.start)
        if self.end:
            existing_query['__key__ <='] = db.Key(self.end)
        existing_skeys = map(str, existing_query.Get(1000))
        to_be_deleted = [k for k in existing_skeys if k not in self.keys]
        datastore.Delete(to_be_deleted)
        to_put=[]
        for e in self.iter_entities():
            local_key(e)
            to_put.append(e)
        datastore.Put(to_put)

