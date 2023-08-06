# Copyright 2008 Adam Byrtek
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

""" Reject files with given extensions that include leading tabs. """

import re

def run(trans, config):
    check = config.getArray("RejectTabs.CheckFiles", [".*"])
    ignore = config.getArray("RejectTabs.IgnoreFiles", [])
    files = trans.getFiles(check, ignore)

    errors = []
    for filename, attr in files.iteritems():
        if attr not in ["A", "U"]:
            # Process only files which were added or updated
            next
        if trans.hasProperty("svn:mime-type", filename) and trans.getProperty("svn:mime-type", filename) == "application/octet-stream":
            # Skip binary files
            next

        file = open(trans.getFile(filename), "r")
        try:
            for line in file:
                if re.match("^\s*\t", line):
                    errors.append("File %s contains leading tabs" % filename)
        finally:
            file.close()

    if len(errors) == 0:
        return ("", 0)
    else:
        return ("\n".join(errors), 1)
