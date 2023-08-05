#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - Config.py
#
# Class to work with the configuration.
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

"""Class to work with the configuration."""

import ConfigParser

import os.path
import re

ConfigParser.DEFAULTSECT = "Default"

class Config(ConfigParser.ConfigParser):
    def __init__(self, transaction):
        """Initialize the Config object"""
        ConfigParser.ConfigParser.__init__(self)
        configFile = os.path.join(transaction.getReposPath(), "hooks", "svncheckerconfig.ini")
        if not os.path.exists(configFile):
            raise "File not found: %s" % configFile
        self.read(os.path.join(transaction.getReposPath(), "hooks", "svncheckerconfig.ini"))
        self.__setProfile(transaction.getFiles())
    
    def __setProfile(self, files):
        """Set the current profile"""
        profile = ConfigParser.DEFAULTSECT
        for section in self.sections():
            matches = True
            regex = re.compile(self.get(section, "Main.Regex"))
            for file, attribute in files.iteritems():
                if not regex.match(file):
                    matches = False
            if matches == True:
                profile = section
        self.profile = profile

    def __getVar(self, var):
        """Returns a variable"""
        if self.has_option(self.profile, var):
            value = self.get(self.profile, var)
        elif self.has_option(self.profile, "Main." + var.split(".")[1]):
            value = self.get(self.profile, "Main." + var.split(".")[1])
        elif self.has_option(ConfigParser.DEFAULTSECT, var):
            value = self.get(ConfigParser.DEFAULTSECT, var)
        else:
            value = self.get(ConfigParser.DEFAULTSECT, "Main." + var.split(".")[1])
        return value

    def getString(self, String):
        """Return a variable as String"""
        return self.__getVar(String)
    
    def getArray(self, String):
        """Return a variable as Array"""
        string = self.__getVar(String)
        vars = string.split(",")
        for var in vars:
            var.strip()
            if var == "":
                vars.remove(var)
        return vars
    
    def getBoolean(self, String):
        """Return a variable as Boolean"""
        var = self.__getVar(String)
        if var == "true":
            return true
        elif var == "false":
            return false
        raise ValueError, 'Not a boolean: %s' % var
    
    def getInteger(self, String):
        """Return a variable as Integer"""
        var = self.__getVar(String)
        return int(var)
