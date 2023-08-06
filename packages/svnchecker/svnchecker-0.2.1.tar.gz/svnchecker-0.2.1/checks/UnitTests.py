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
This check tests if a unit test exists for a given Java class.
The java class must follow the pattern /main/.../Class.java and
the unit test  must follow the pattern /main/.../TestClass.java. 
Interfaces are omitted.
"""

import re

def run(transaction, config):

    check = config.getArray("UnitTests.CheckFiles", [".*\.java"])
    ignore = config.getArray("UnitTests.IgnoreFiles", [])
    files = transaction.getFiles(check, ignore)

    interfacePattern = re.compile("interface .* {")
    classPattern = re.compile("class .* {")

    msg = ""
    for filename, attribute in files.iteritems():
        if attribute in ["A", "U", "UU"] and not "/test/" in filename:

            # skip java interfaces
            fileHandler = open(transaction.getFile(filename), "r")
            skipFile = False
            for line in fileHandler:
                if interfacePattern.search(line):
                    skipFile = True
                    break
                elif classPattern.search(line):
                    break
            fileHandler.close()
            
            if skipFile:
                continue

            unitTestName = filename.replace("/main/", "/test/").replace(".java", "Test.java")

            if not transaction.fileExists(unitTestName):
                msg += "No unittest exists for file %r.\n" % filename

    if msg:
        return (msg, 1)
    else:
        return ("", 0)
