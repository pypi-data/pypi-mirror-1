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

""" Checks XML files for correctness. """

from xml.dom import minidom
from xml.parsers import expat

def run(transaction, config):

    check = config.getArray("XMLValidator.CheckFiles", [".*\.xml"])
    ignore = config.getArray("XMLValidator.IgnoreFiles", [])
    files = transaction.getFiles(check, ignore)

    msg= ""
    for filename, attribute in files.iteritems():
        if attribute in ["A", "U"]:
            try:
                minidom.parse(transaction.getFile(filename))
            except expat.ExpatError, e:
                msg += "XML Validation error in file %r: %s" % (filename, e)

    if msg:
        return (msg, 1)
    else:
        return ("", 0)
