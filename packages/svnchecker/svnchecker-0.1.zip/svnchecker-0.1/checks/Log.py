#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - Log.py
#
# Create a log message.
#
# Created: 03/01/2006 Heinrich Wendel <heinrich.wendel@dlr.de>
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

"""Create a log message"""

import datetime

class Check:
    def main(self, transaction, config):
        files = transaction.getFiles()
        msg = "Date: " + datetime.datetime.now().strftime("%H:%M - %d.%m.%Y") + "\n"
        msg += "Author: " + transaction.getUserID() + "\n"
        #msg += "Repository: " + transaction.getReposPath() + "\n"
        msg += "Revision: " + transaction.getRevision() + "\n"
        
        msg += "\n"
        
        msg += config.getString("Log.SvnWebUrl") + "\n"
        
        msg += "\n"
        
        msg += "Modified Files:\n"
        for file, attribute in files.iteritems():
            msg += "%s\t%s\n" % (attribute, file)

        msg += "\n"
        
        msg += "Log Message:\n"
        msg += transaction.getCommitMsg()
        msg += "\n"

        return (msg, 0)
    