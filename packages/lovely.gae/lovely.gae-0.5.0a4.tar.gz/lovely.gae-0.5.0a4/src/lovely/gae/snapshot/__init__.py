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

from lovely.gae.snapshot import models
from google.appengine.ext import webapp
from google.appengine.api import datastore_admin

class API(object):

    def get_kinds(self, excludes=['Snapshot', 'RangeBackup']):
        """returns the available kinds in current datastore, without excludes"""
        schema = datastore_admin.GetSchema()
        kinds = []
        for entity_proto in schema:
            kind = entity_proto.key().path().element_list()[-1].type()
            if kind not in excludes:
                kinds.append(kind)
        kinds.sort()
        return kinds

    def create_snapshot(self, kinds=None):
        kinds = kinds or self.get_kinds()
        return models.Snapshot.create(kinds)

    def restore_snapshot(self, s_key):
        s = models.Snapshot.get(s_key)
        s.restore()

api = API()

class CreateSnapshotHandler(webapp.RequestHandler):

    def get(self):
        kinds = self.request.get_all('kinds') or None
        s = api.create_snapshot(kinds=kinds)
        self.response.headers['Content-Type'] = 'text/plain'
        print >> self.response.out, 'Created Snapshot %s' % s.key().id_or_name()
        print >> self.response.out, 'Kinds: %s' % s.kinds


HANDLER_TUPLES = (
    ('/lovely.gae/snapshot.CreateSnapshotHandler', CreateSnapshotHandler),
    )

def getApp(debug=True):
    return webapp.WSGIApplication(HANDLER_TUPLES, debug=debug)
