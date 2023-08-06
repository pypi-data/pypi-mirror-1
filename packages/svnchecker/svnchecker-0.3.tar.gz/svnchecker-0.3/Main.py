#!/usr/bin/env python

# pylint: disable-msg=W0122, E0602

# Copyright 2008 German Aerospace Center (DLR)
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

"""
http://svnchecker.tigris.org
"""

import os
import sys

from modules import Config, Transaction

# initialize configuration and transaction
try:
    hook = sys.argv[1]
    reposPath = sys.argv[2]
    txnName = sys.argv[3]

    if hook not in ["PreCommit", "PostCommit"]:
        raise IndexError()

except IndexError:
    sys.stderr.write("""Usage: Main.py hook reposPath txnName
       hook: PreCommit or PostCommit
       reposPath: the path to this repository
       txnName: the name of the transaction about to be committed\n""")
    sys.exit(1)

os.chdir(os.path.join(reposPath, "hooks"))

transaction = Transaction.Transaction(reposPath, txnName)

def finish(code):
    transaction.cleanup()
    sys.exit(code)


configFilename = "svncheckerconfig.ini"
localConfig = os.path.join(reposPath, "hooks", configFilename)
globalConfig =  os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), configFilename)
config = Config.Config(globalConfig, localConfig)
config.setHooksLocation(os.path.join(reposPath, "hooks"))

# which files do not belong to a profile
files = transaction.getFiles().keys()
toRemove = []
for profile in config.getProfiles():
    config.setProfile(profile)
    transaction.setProfile(config.getString('Main.Regex', "^$"))
    toRemove += [filename for filename in transaction.getFiles() if filename in files]

for filename in toRemove:
    files.remove(filename)

default = "^("
for filename in files:
    default += filename + "|"
default = default.strip("|")
default += ")$"


for profile in config.getProfiles() + [Config.DEFAULTSECT]:

    config.setProfile(profile)
    if profile == Config.DEFAULTSECT:
        transaction.setProfile(default)
    else:
        transaction.setProfile(config.getString('Main.Regex', "^$"))

    # if there are no files in this profile continue
    if len(transaction.getFiles()) == 0:
        continue

    # run the configured checks
    for check in config.getArray('Main.%sChecks' % hook):
        exec("from checks.%s import run" % check)
        (msg, exitCode) = run(transaction, config)

        if not msg:
            continue

        if exitCode == 1:
            handlers = config.getArray('%s.FailureHandlers' % check)
        else:
            handlers = config.getArray('%s.SuccessHandlers' % check)

        # run the configured handlers
        for handler in handlers:
            exec("from handlers.%s import run" % handler)
            run(transaction, config, check, msg, exitCode)

        if exitCode == 1:
            finish(exitCode)

finish(0)
