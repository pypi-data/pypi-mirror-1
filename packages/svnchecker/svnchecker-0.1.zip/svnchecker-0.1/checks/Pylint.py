#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - Checkstyle.py
#
# Checks python files for coding style.
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

"""Checks python files for coding style."""

from modules import Process
import os
import tempfile

class Check:
    def main(self, transaction, config):

        os.putenv("PYLINTHOME", tempfile.gettempdir())

        check = config.getArray("Pylint.CheckFiles")
        ignore = config.getArray("Pylint.IgnoreFiles")
        files = transaction.getFiles(check, ignore)

        pylint = config.getString("Pylint.Pylint")
        checks = config.getString("Pylint.ConfigFile")

        command = "%s --rcfile %s " % (pylint, checks)
        
        for file, attribute in files.iteritems():
            if attribute in ["A", "U", "UU"]:
                output = Process.execute(command + transaction.getFile(file))
                if output:
                    msg = "Coding style error in file '%s'\n\n" % file
                    msg += "\n".join(output)
                    return (msg, 1)

        return ("", 0)
