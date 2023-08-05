#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - File.py
#
# Log the message into a file.
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

"""Log the message into a file"""

class Handler:
    """Handler Class"""
    
    def main(self, transaction, config, module, msg, exitCode):
        """Main Function"""
              
        if (exitCode == 1):
            file = config.getString("%s.FailureFile" % module)
        else:
            file = config.getString("%s.SuccessFile" % module)
            
        fd = open(file, "a")
        fd.write(msg)
        fd.write("\n====================\n")
        fd.close()