#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - MantisModule.py
#
# Class that handles access to the Mantis DB.
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

"""Class that handles access to the Mantis DB."""

import SOAPpy
import sys

class MantisModule:
    """MantisModule Class."""
    
    def __init__(self, config):
        """Initialize the MantisModule object."""
        url = config.getString('Mantis.URL')
        self.service = SOAPpy.SOAPProxy(url)
        self.user = config.getString('Mantis.User')
        self.pw = config.getString('Mantis.Password')

    def issueExists(self, bugID):
        """Return whether a bug exists."""
        result = self.service.mc_issue_exists(self.user, self.pw, bugID)
        if result == 0:
            return False
        else:
            return True
            
    def issueGetStatus(self, bugID):
        """Return the status of a bug."""
        result = self.service.mc_issue_get(self.user, self.pw, bugID)
        return result.status[1]
    
    def issueGetHandler(self, bugID):
        """Return the handler of a bug."""
        result = self.service.mc_issue_get(self.user, self.pw, bugID)
        return result.handler.name
    
    def issueAddNote(self, bugID, note):
        """Adds a note to a bug."""
        self.service.mc_issue_note_add(self.user, self.pw, bugID, {'text': note})
        
    def issueSetCustomField(self, bugID, name, value):
        """Sets the value of a field."""
        result = self.service.mc_issue_get(self.user, self.pw, bugID)
        
        if result.custom_fields:
            for i in range(len(result.custom_fields)):
                if result.custom_fields[i]['field']['name'] == name:
                    result.custom_fields[i].value = value
                    result.reporter.id = 0
                    result.reporter.name = ""
                    result.reporter.email = ""
                    break
        
        self.service.mc_issue_update(self.user, self.pw, bugID, result)
    
    def issueHasCustomField(self, bugID, name):
        """Checks whether a bug has a specified custom field."""
        result = self.service.mc_issue_get(self.user, self.pw, bugID)
        
        if result.custom_fields:
            for field in result.custom_fields:
                if field['field']['name'] == name:
                    return True
        
        return False