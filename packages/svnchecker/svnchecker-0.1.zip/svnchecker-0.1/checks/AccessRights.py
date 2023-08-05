#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - AccessRights.py
#
# Check access rights on files.
#
# Created: 08/15/2006 Heinrich Wendel <heinrich.wendel@dlr.de>
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

"""Check access rights on files."""

from modules import Process

import ConfigParser

import sys
    
class Check:
    def main(self, transaction, config):

        rules = config.getArray("AccessRights.Rules")
        failure = []
        
        for rule in rules:

            check = config.getArray("AccessRights.%s.CheckFiles" % rule)
            ignore = config.getArray("AccessRights.%s.IgnoreFiles" % rule)
            files = transaction.getFiles(check, ignore)
        
            try:
                allows = config.getArray("AccessRights.%s.AllowUsers" % rule)
            except ConfigParser.NoOptionError:
                allows = None
            
            try:
                denies = config.getArray("AccessRights.%s.DenyUsers" % rule)
            except ConfigParser.NoOptionError:
                denies = None
                
                
            for file, attribute in files.iteritems():
                if allows and transaction.getUserID() not in allows:
                    failure.append(file)
                if denies and transaction.getUserID() in denies:
                    failure.append(file)
  
        if failure:
            msg = "You don't have rights to edit these files: \n"
            msg += "\n".join(failure)
            return (msg, 1)

        return ("", 0)
