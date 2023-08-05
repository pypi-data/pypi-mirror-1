#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - main.py
#
# Controller script for the svnchecker
#
# Created: 02/22/2006 Heinrich Wendel <heinrich.wendel@dlr.de>
# Changed:
#
# Copyright 2006 Deutsches Zentrum für Luft- und Raumfahrt e.V. (DLR)
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
#----------------------------------------------------------------------------

"""
https://wiki.sistec.dlr.de/SVNChecker
"""

__version__ = 1.0

import sys
import os

# debug this remotly 
# http://www.fabioz.com/pydev/manual_adv_remote_debugger.html
#PYDEV_DEBUGGER = r"/work/hinz_ja/install/pydev_remote_debugger/pysrc"
#sys.path.insert(0, PYDEV_DEBUGGER)
#import pydevd
#pydevd.settrace('129.247.51.77')

from modules.Config import Config
from modules.Transaction import Transaction

# init configuration and transaction
try:
    hook = sys.argv[1]
    reposPath = sys.argv[2]
    txnName = sys.argv[3]
except IndexError:
    sys.stderr.write("""Usage: Main.py hook reposPath txnName
       hook: PostCommit or PreCommit
       reposPath: the path to this repository
       txnName: the name of the txn about to be committed\n""")
    sys.exit(1)

transaction = Transaction(reposPath, txnName)
config = Config(transaction)

# change workdir
os.chdir(os.path.join(reposPath, "hooks"))

# get a list of configured checks
checks = config.getArray('Main.%sChecks' % hook)

for check in checks:
    
    #import the configured checks
    exec("from checks.%s import Check" % check)
    # all classes in module 'checks' are named Check 
    checkclass = Check()
    (msg, exitCode) = checkclass.main(transaction, config)
        
    # execute enabled handlers
    if (exitCode == 0):
        handlers = config.getArray('%s.SuccessHandlers' % check)
    else:
        handlers = config.getArray('%s.FailureHandlers' % check)
        
    for handler in handlers:
        exec("from handlers.%s import Handler" % handler)
        handlerclass = Handler()
        handlerclass.main(transaction, config, check, msg, exitCode)
        
    if exitCode == 1:
        sys.exit(1)
