#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - CheckKeywords.py
#
# This script checks if the svn:keywords for added files are set.
#
# Created: Jan Hinzmann 2006.06.02 14:44 CET
# Changed:
# Depends: Python 2.4 (Python 2.3: 'import sets', Python 2.2: use backports)
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

from modules import Process

class Check:
    
    def main (self, transaction, config) :
        """
        1. get info about changes
        2. iterate over changeset getting svn:keywords using svnlook
        3. if one file has not set the right keywords: return (msg, 1)
        """

        check = config.getArray("Keywords.CheckFiles")
        ignore = config.getArray("Keywords.IgnoreFiles")
        files = transaction.getFiles(check, ignore)

        keywordsShould = config.getArray("Keywords.Keywords")
        keywordsMissing = []
        
        for file, attribute in files.iteritems():     
            if attribute in ["A", "U", "_U", "UU"]:
                keywordsIs = transaction.getKeyword("svn:keywords", file)
                
                for keyword in keywordsShould:
                    if keyword not in keywordsIs:
                        keywordsMissing.append(keyword)
                
                if len(keywordsMissing):
                    msg =  "No keys, no commit!\n"
                    msg += "Try: svn propset svn:keywords \"%s\" %s\n" % (" ".join(keywordsShould), file)              
                    return (msg, 1)

        return ("", 0)
