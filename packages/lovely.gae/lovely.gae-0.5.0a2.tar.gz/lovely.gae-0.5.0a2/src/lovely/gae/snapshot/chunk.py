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

from google.appengine.ext import db
import hashlib
from StringIO import StringIO

CHUNK_SIZE = 1024*(1024-128)

class Data(db.Model):

    chunks = db.StringListProperty()
    length = db.IntegerProperty()

    @classmethod
    def store(cls, data):
        mf = hashlib.sha1(data)
        dkn = u'sha1:%s' % mf.hexdigest()
        existing = Data.get_by_key_name(dkn)
        if existing:
            return existing
        data = StringIO(data)
        chunks = []
        l = 0
        while True:
            d = data.read(CHUNK_SIZE)
            if not d:
                break
            key_name = u'sha1:%s' % hashlib.sha1(d).hexdigest()
            chunk = Chunk.get_by_key_name(key_name)
            if not chunk:
                chunk = Chunk(key_name=key_name, data=d)
                chunk.put()
            chunks.append(key_name)
            l+=len(d)
        f = Data(key_name=dkn, chunks=chunks, length=l)
        f.put()
        return f

    def __repr__(self):
        return '<Data %s>' % self.key().name()

    def __len__(self):
        return self.length

    def get_data(self):
        if not hasattr(self, '_v_data'):
            self._v_data = StringIO()
            for name in self.chunks:
                chunk = Chunk.get_by_key_name(name)
                self._v_data.write(chunk.data)
        self._v_data.seek(0)
        return self._v_data

class Chunk(db.Model):

    data = db.BlobProperty()

    def __len__(self):
        return len(self.data)

