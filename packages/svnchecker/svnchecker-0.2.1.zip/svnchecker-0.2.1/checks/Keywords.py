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
Checks for svn:keywords on all added files in this commit.
 
subversion knows the following keywords for substitution:
svn:keywords  also known as
=======================================
Date          LastChangeDate
Revision      LastChangedRevision | Rev
Author        LastChangedBy
HeadURL       URL
Id
"""

from modules.Transaction import PropertyNotFoundException

def run(transaction, config) :

    check = config.getArray("Keywords.CheckFiles", [".*"])
    ignore = config.getArray("Keywords.IgnoreFiles", [])
    files = transaction.getFiles(check, ignore)

    msg = ""
    keywordsShould = config.getArray("Keywords.Keywords")

    for filename, attribute in files.iteritems():
        if attribute in ["A", "U", "_U", "UU"]:
            try:
                keywordsIs = transaction.getProperty("svn:keywords", filename)
            except PropertyNotFoundException:
                keywordsIs = ""

            for keyword in keywordsShould:
                if keyword not in keywordsIs:
                    msg += "Missing keyword %r on file %r.\n" % (keyword, filename) 

    if msg:
        return (msg, 1)
    else:
        return ("", 0)
