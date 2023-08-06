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

""" Checks Java files for coding style errors using Checkstyle. """

from modules import Process

def run(transaction, config):

    check = config.getArray("Checkstyle.CheckFiles", [".*\.java"])
    ignore = config.getArray("Checkstyle.IgnoreFiles", [])
    files = transaction.getFiles(check, ignore)

    java = config.getString("Checkstyle.Java")
    classpath = config.getString("Checkstyle.Classpath")
    config = config.getString("Checkstyle.ConfigFile")

    command = "%s -classpath %s com.puppycrawl.tools.checkstyle.Main -c %s " % (java, classpath, config)

    files = [transaction.getFile(oneFile[0]) for oneFile in files.iteritems() if oneFile[1] in ["A", "U", "UU"]]

    try:
        Process.execute(command + " ".join(files))
    except Process.ProcessException, e:
        msg = "Coding style errors found:\n\n"
        msg += e.output + "\n"
        msg += "See Checkstyle documentation for a detailed description: http://checkstyle.sourceforge.net/"
        return (msg, 1)

    return ("", 0)
