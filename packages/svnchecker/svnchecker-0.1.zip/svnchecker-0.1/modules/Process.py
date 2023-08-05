#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - Process.py
#
# Execute a Process and return the message.
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

"""Execute a Process and return the message."""

import os

pathcmd = "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin "

class ProcessException(Exception):
    def __init__(self, command, exitCode, message):
        self.command = command
        self.message = message
        
    def __str__(self):
        return "Command '%s' exited with exitCode %s\n%s" % (self.command, self.exitCode, self.getOutput())
    
    def __repr__(self):
        return self.__str__()
    
    def getOutput(self):
        output = ""
        for line in self.message:
            output += line
        return output
    

def execute(command):
    stdout = os.popen(pathcmd + command + " 2>&1")
    message = stdout.readlines()
    exitCode = stdout.close()
    
    if (exitCode != None):
        raise ProcessException(command, exitCode, message)
    else:
        return message
    