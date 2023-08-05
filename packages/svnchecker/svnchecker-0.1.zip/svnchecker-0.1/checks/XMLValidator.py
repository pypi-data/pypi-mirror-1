#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - XMLValidator.py
#
# Checks xml files for correctness and against dtd and schema.
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

"""Checks xml files for correctness and against dtd and schema."""

from modules import Process
import sys
    
class Check:
    def main(self, transaction, config):

        check = config.getArray("XMLValidator.CheckFiles")
        ignore = config.getArray("XMLValidator.IgnoreFiles")
        files = transaction.getFiles(check, ignore)

        java = config.getString("XMLValidator.Java")
        classpath = config.getString("XMLValidator.Classpath")
        
        command = "%s -classpath %s sax.Counter -v -s -f " % (java, classpath)
        
        for file, attribute in files.iteritems():
            if attribute in ["A", "U"]:
                output = Process.execute(command + transaction.getFile(file))
                if "Error" in output[0]:
                    msg = "XML Validation error in file '%s'\n\n" % file
                    msg += "\n".join(output) + "\n"
                    return (msg, 1)

        return ("", 0)
