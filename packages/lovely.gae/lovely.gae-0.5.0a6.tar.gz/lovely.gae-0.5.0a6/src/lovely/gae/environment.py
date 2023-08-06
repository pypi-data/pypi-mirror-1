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

import os
import sys
import logging

_log = logging.getLogger(__name__)

def BREAKPOINT():
    import pdb
    st = pdb.Pdb(None, sys.__stdin__, sys.__stdout__).set_trace
    st()

def add_appengine_paths(project_dir=None):
    try:
        import google.appengine
    except ImportError:
        SDK_PATH = '.'
        for path in os.environ.get('PATH', '').split(':'):
            path = os.path.realpath(path.strip())
            if path.endswith('google_appengine') and os.path.isdir(
                os.path.join(path, 'google')):
                SDK_PATH = path
                break
        dev_appserver = os.path.join(SDK_PATH, 'dev_appserver.py')
        globs = dict(__file__=dev_appserver)
        execfile(dev_appserver, globs)
        sys.path = globs['EXTRA_PATHS'] +  sys.path
    try:
        import google.appengine
    except ImportError:
        sys.stderr.write("The Google App Engine SDK could not be found!\n")


def setUp(project_dir=None):
    add_appengine_paths()
