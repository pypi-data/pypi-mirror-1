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

import cPickle as pickle
import getpass
import os
import sys
from optparse import OptionParser
import time
from google.appengine.ext.remote_api import remote_api_stub

from lovely.gae.environment import add_appengine_paths
from lovely.gae.snapshot import models
from google.appengine.ext import db

add_appengine_paths()

def auth_func():
    return raw_input('Username:'), getpass.getpass('Password:')


def download_snapshot(out_dir, snapshot_id=None):
    if snapshot_id:
        snapshot = models.Snapshot.get_by_id(snapshot_id)
    else:
        snapshot = models.Snapshot.all().order('-__key__').get()
    if not snapshot:
        raise RuntimeError, 'No Snapshot found %r' % snapshot_id
    out = os.path.join(out_dir, 'snapshot.%s' % snapshot.key().id_or_name())

    if os.path.exists(out):
        raise RuntimeError, 'Out file exists %r' % out

    print "Downloading snapshot: %s" % snapshot.key().id_or_name()
    rbks = models.RangeBackup.all(keys_only=True).order('__key__').filter(
        'snapshot', snapshot.key()).fetch(1000)
    num_rbs = len(rbks)
    entities = []
    start_time = time.time()
    avg_time=1.0
    for i, rbk in enumerate(rbks):
        # bug in remote api, we have an emtpy entity here see
        # http://code.google.com/p/googleappengine/issues/detail?id=1780
        if not isinstance(rbk, db.Key):
            rbk = rbk.key()
        print "Downloading %s pos: %s/%s remaining: %.1f seconds" % (
            rbk.id_or_name(), i+1, num_rbs, avg_time*(num_rbs-i))
        for t in range(3):
            try:
                rb = db.get(rbk)
                break
            except Exception ,e:
                print >> sys.stderr, "Failure try", t+1, e
                time.sleep(t+1)
        for e in rb.iter_entities():
            entities.append(e._ToPb().Encode())
        avg_time = (time.time()-start_time)/(i+1)
    print "Saving to %s" % out
    out = file(out, 'wb')
    pickle.dump(entities, out)
    out.close()
    return out.name

def download_script(argv=None):
    argv = argv or sys.argv
    parser = OptionParser(
            usage="usage: %s outdir" % argv[0])
    parser.add_option("-H", "--host",
                      dest="host",
                      help="The host to connect to.")
    parser.add_option("-a", "--app_id",
                      dest="app_id",
                      help="The application id to use")
    parser.add_option("-i", "--snapshot_id",
                      type="int",
                      dest="snapshot_id",
                      help="The snapshot id to download, if omitted the latest snapshot is used")

    options, args = parser.parse_args(argv[1:])
    if len(args)!=1:
        print >> sys.stderr, "invalid arguments"
        sys.exit(1)
    out_dir, = args
    out_dir = os.path.abspath(out_dir)
    if not os.path.isdir(out_dir):
        raise RuntimeError, "%s is not a directory" % out_dir
    remote_api_stub.ConfigureRemoteDatastore(
        options.app_id, '/remote_api', auth_func, options.host)
    download_snapshot(out_dir, snapshot_id=options.snapshot_id)
