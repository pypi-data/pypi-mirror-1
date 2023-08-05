#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - Mantis.py
#
# Checks if a log message contains a valid MANTIS ID.
#
# Created: 03/03/2006 Heinrich Wendel <heinrich.wendel@dlr.de>
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
Checks if a log message contains a valid MANTIS ID,
with a MANTIS ID <#> that is set to status 'in_progress'.
"""

from modules import MantisModule
import re

class Check:
    """Check Class."""
    
    def main(self, transaction, config):
        """Main function."""
        
        mantis = MantisModule.MantisModule(config)

        logMessage = transaction.getCommitMsg()
        pattern = re.compile('^MANTIS ID ([0-9]+)\n(.+)?')
        result = pattern.match(logMessage)
        
        if result == None:
            msg = "Invalid log message: The message must contain 'MANTIS ID <#>'!"
            return (msg, 1)
        else:
            issueId = result.group(1)
            
            if not mantis.issueExists(issueId):
                msg = "MANTIS ID %s not found!" % issueId
                return (msg, 1)
            else:
                status = mantis.issueGetStatus(issueId)
                if status != "in_progress":
                    msg = "MANTIS ID %s is not 'in_progress'!" % issueId
                    return (msg, 1)
        
                user = transaction.getUserID()
                handler = mantis.issueGetHandler(issueId)
                
                if (user != handler):
                    msg = "You are not the handler of MANTIS ID %s!" % issueId
                    return (msg, 1)
        
        return ("", 0)