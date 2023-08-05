#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - UnitTests.py
#
# Checks if a unit test exists.
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

"""Checks java files for coding style."""

from modules import Process
import sys

class Check:
    def main(self, transaction, config):

        check = config.getArray("UnitTests.CheckFiles")
        ignore = config.getArray("UnitTests.IgnoreFiles")
        files = transaction.getFiles(check, ignore)
        
        for file, attribute in files.iteritems():
            if attribute in ["A", "U", "UU"] and not "test/" in file:
                
                # Interface?
                fileHandler = open(transaction.getFile(file), "r")
                skipFile = False
                while 1:
                    line = fileHandler.readline()
                    if "{" in line:
                        if "interface" in line:
                            skipFile = True
                        break
                    if not line:
                        break
                fileHandler.close()
                if skipFile == True:
                    continue
                
                if not file.replace("/main/", "/test/").replace(".java", "Test.java")  in files \
                 and not transaction.fileExists(file.replace("/main/", "/test/").replace(".java", "Test.java")):
                    msg = "No unittest exists for file '%s'.\n" % file
                    return (msg, 1)

        return ("", 0)
