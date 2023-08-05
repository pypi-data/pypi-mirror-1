#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - Checkstyle.py
#
# Checks java files for coding style.
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

class Check:
    def main(self, transaction, config):

        check = config.getArray("Checkstyle.CheckFiles")
        ignore = config.getArray("Checkstyle.IgnoreFiles")
        files = transaction.getFiles(check, ignore)

        java = config.getString("Checkstyle.Java")
        classpath = config.getString("Checkstyle.Classpath")
        checks = config.getString("Checkstyle.ConfigFile")
        
        # check out checks.xml and suprresions.xml from subversion itself
        # nice idea but currently not doable
        # checks = transaction.getFile(config.getString("Checkstyle.ConfigFile"))
        # supressions = transaction.getFile(config.getString("Checkstyle.SupressionsFile"))
        # if supressions:
        #    Process.execute("sed -i -e s:supressions.xml:%s: %s" % (supressions, supressions))

        command = "%s -classpath %s com.puppycrawl.tools.checkstyle.Main -c %s " % (java, classpath, checks)
        
        for file, attribute in files.iteritems():
            if attribute in ["A", "U", "UU"]:
                try:
                    output = Process.execute(command + transaction.getFile(file))
                except Process.ProcessException, e:
                    msg = "Coding style error in file '%s'\n\n" % file
                    msg += e.getOutput() + "\n"
                    msg += "See Checkstyle documentation for a detailed description: http://checkstyle.sourceforge.net/"
                    return (msg, 1)

        return ("", 0)
