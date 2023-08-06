# pylint: disable-msg=W0201, W0704

# Copyright 2008 German Aerospace Center (DLR)
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

""" Class to work with the configuration. """


import os.path
import ConfigParser

DEFAULTSECT = "Default"
ConfigParser.DEFAULTSECT = DEFAULTSECT


class NoSuchConfigurationValueError(Exception):
    def __init__(self, var):
        Exception.__init__(self, """Could not find configuration option %r in the configuration files.
Please take a look at the documentation for a description of this option.""" % var)


class Config:
    def __init__(self, globalConfigFilename, localConfigFilename):
        """ Initialize the Config object. """

        self.configFiles = []

        configFilenames = [globalConfigFilename, localConfigFilename]
        
        for filename in configFilenames:
            if filename is not None and os.path.exists(filename):
                try:
                    configFile = ConfigParser.ConfigParser()
                    configFile.read(filename)
                    self.configFiles.append(configFile)
                except ConfigParser.ParsingError:
                    pass

        if len(self.configFiles) == 0:
            raise Exception("""Could not find a valid configuration file named svncherconfig.ini.
You can use a global file in your svnchecker directory and/or a local one in your hooks directory.""")

        self.profile = ConfigParser.DEFAULTSECT
        self.hooksLocation = ""

    def __getVar(self, var):
        """ This is the variable resolver. """
        if not "." in var:
            raise NoSuchConfigurationValueError(var)

        value = None

        for configFile in self.configFiles:
            if configFile.has_option(self.profile, var):
                value = configFile.get(self.profile, var)
            elif configFile.has_option(self.profile, "Main." + var.split(".")[1]):
                value = configFile.get(self.profile, "Main." + var.split(".")[1])
            elif configFile.has_option(ConfigParser.DEFAULTSECT, var):
                value = configFile.get(ConfigParser.DEFAULTSECT, var)
            elif configFile.has_option(ConfigParser.DEFAULTSECT, "Main." + var.split(".")[1]):
                value = configFile.get(ConfigParser.DEFAULTSECT, "Main." + var.split(".")[1])

            if value is not None:
                break

        if value is not None:
            return value.replace("%HOOKS%", self.hooksLocation)
        else:
            raise NoSuchConfigurationValueError(var)

    def setHooksLocation(self, location):
        """
        Sets the repository location in order to replace %HOOKS% by it in the returned values.
        """
        self.hooksLocation = location

    def setProfile(self, profile):
        """
        Sets the used profile.
        Do NOT use in your checks or handlers.
        """
        self.profile = profile

    def getProfiles(self):
        """
        Returns the available profiles.
        Do NOT use in your checks or handlers.
        """
        sections = []
        for configFile in self.configFiles:
            for section in configFile.sections():
                if section not in sections and section != ConfigParser.DEFAULTSECT:
                    sections.append(section)
        return sections

    def getString(self, var, default=None):
        """
        Returns a variable as string. If the
        variable does not exist and default is
        set default will be returned, otherwise
        a NoSuchConfigurationValueError will be
        raised.
        """
        try:
            return self.__getVar(var)
        except NoSuchConfigurationValueError, e:
            if default is not None:
                return default
            else:
                raise e

    def getArray(self, var, default=None):
        """
        Returns a variable as array. The
        configuration string is split by the ','
        character. If the variable does not
        exist and default is set default will be
        returned, otherwise a
        NoSuchConfigurationValueError will be
        raised.
        """
        try:
            string = self.__getVar(var)
            return [x.strip() for x in string.split(",") if x.strip() != ""]
        except NoSuchConfigurationValueError, e:
            if default is not None:
                return default
            else:
                raise e

    def getBoolean(self, var, default=None):
        """ 
        Returns a variable as boolean. True,
        true, 1 will return True. False, false,
        0 will return False. If the variable
        does not match the pattern a ValueError
        will be raised.If the variable does not
        exist and default is set default will be
        returned, otherwise a
        NoSuchConfigurationValueError will be
        raised.
        """
        try:
            var = self.__getVar(var)
            if var in ["True", "true", "1"]:
                return True
            elif var in ["False", "false", "0"]:
                return False
            raise ValueError('Not a boolean: %s' % var)
        except NoSuchConfigurationValueError, e:
            if default is not None:
                return default
            else:
                raise e

    def getInteger(self, var, default=None):
        """
        Returns a variable as integer. If the
        variable cannot be converted to an
        integer a ValueError will be raised. If
        the variable does not exist and default
        is set default will be returned,
        otherwise a
        NoSuchConfigurationValueError will be
        raised.
        """
        try:
            var = self.__getVar(var)
            return int(var)
        except NoSuchConfigurationValueError, e:
            if default is not None:
                return default
            else:
                raise e
