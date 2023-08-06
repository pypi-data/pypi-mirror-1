#!/usr/bin/env python
#
# Copyright 2009 Matthew Wilkes
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

import tempfile, os, sys, thread
from google.appengine.tools import dev_appserver

threads = []

def enableEphemeralStorage():
    datastore = tempfile.NamedTemporaryFile()
    datastore_path = datastore.name
    def useEphemeralDatastore(func, directory):
        def _func(app_id, **config):
            config['datastore_path'] = directory
            config['clear_datastore'] = True
            return func(app_id, **config)
        return _func

    dev_appserver.SetupStubs = useEphemeralDatastore(
                               dev_appserver.SetupStubs,
                               datastore_path
                            )
  
  
def withEphemeralStorage(func):
    def _func(path):
        enableEphemeralStorage()
        return func(path)
    return _func

def run(path):
    from google.appengine.tools import dev_appserver_main 
    path = os.path.abspath(path)
    return dev_appserver_main.main((None, path,))

def asThread(func):
    def _func(*args):
        if threads:
            return # Force only one HTTP Server
        import signal
        def _signal(sig, act):
            return
        signal.signal = _signal
        threads.append(thread.start_new_thread(func, args))
        # Block for a couple of seconds to give the thread chance to start
        import time
        time.sleep(2)
    return _func

def pathAsArgv1(func):
    def _func():
        return func(sys.argv[1])
    return _func

consoleRunWithEphemeralStorage = pathAsArgv1(withEphemeralStorage(run))
consoleRun = pathAsArgv1(run)
testingRunWithEphemeralStorage = asThread(withEphemeralStorage(run))
testingRun = asThread(run)
