# pylint: disable-msg=W0102, W0704

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

""" Class to work with transactions. """


import os
import re
import shutil
import tempfile

from modules import Process


class FileNotFoundException(Exception):
    def __init__(self, filename):
        Exception.__init__(self, "No such file in repository or transaction %r." % filename)

class PropertyNotFoundException(Exception):
    def __init__(self, keyword, filename):
        Exception.__init__(self, "Property %r for file %r not set." % (keyword, filename))


class Transaction:

    def __init__(self, reposPath, txnName):
        """ Initialize the transaction object. """
        
        txnName = str(txnName)
        try:
            int(txnName)
            self.type = "revision"
        except ValueError:
            self.type = "transaction"
 
        self.reposPath = reposPath
        self.txnName = txnName

        self.profile = re.compile(".*")
        
        self.tmpdir = tempfile.mkdtemp()

        self.cache = {}

    def __executeSVN(self, command, arg = "", split=False):
        command = "svnlook --%s %s %s %s %s" % (self.type, self.txnName, command, self.reposPath, arg)
        if command in self.cache:
            return self.cache[command]
        
        output = Process.execute(command)
        if split:
            output = [x.strip() for x in output.split("\n") if x.strip()]
        
        self.cache[command] = output
        return self.cache[command]

    def cleanup(self):
        """
        Delete the temporary directory.
        Do NOT use in your checks or handlers.
        """
        shutil.rmtree(self.tmpdir)

    def setProfile(self, profile):
        """
        Sets the current profile.
        Do NOT use in your checks or handlers.
        """
        self.profile = re.compile(profile)

    def getUserID(self):
        """ Returns a string with the username of the current transaction. """
        user = self.__executeSVN("author")
        return user.strip()

    def getFiles(self, checkList=[".*"], ignoreList=[]):        
        """
        Returns a map of all modified files. The keys of the map
        are the filenames. The values of the map is the
        associated attribute, which can be one of the default
        svnlook changed attributes: 
        http://svnbook.red-bean.com/en/1.4/svn-book.html#svn.ref.svnlook.c.changed
    
        @param checkList List of regular expressions for files which should be included.
        @param ignoreList List of regular expressions for files which should be ignored.
        """
        output = self.__executeSVN("changed", split=True)
        files = {}
        for entry in output:
            attributes = entry[0:3].strip()
            filename = entry[4:].strip()

            if self.profile.search(filename) and self.__check(filename, checkList) and not self.__check(filename, ignoreList):
                files[filename] = attributes
        return files

    def __check(self, datei, items):
        for item in items:
            regex = re.compile(item)
            if regex.search(datei):
                return True
        return False

    def getFile(self, filename):
        """ Returns the path to a temporary copy of a file in the repository. """
        if not self.fileExists(filename):
            raise FileNotFoundException(filename)

        tmpfilename = os.path.join(self.tmpdir, filename)
        if os.path.exists(tmpfilename):
            return tmpfilename

        content = self.__executeSVN("cat", "\"" + filename + "\"")

        dirname = os.path.dirname(filename)
        tmpdirname = os.path.join(self.tmpdir, dirname)
        if dirname and not os.path.exists(tmpdirname):
            os.makedirs(tmpdirname)

        fd = open(tmpfilename, "w")
        fd.write(content)
        fd.close()

        return tmpfilename

    def fileExists(self, filename, ignoreCase=False):
        """ Returns whether a file exists in the current transaction or revision of the repository, optionally case-insensitive. """
        exists = False

        if ignoreCase:
            filename = filename.lower()
            files = self.__executeSVN("tree", "--full-paths", split=True)
            count = 0
            for fname in files:
                if fname.lower() == filename:
                    count += 1
                    if count >= 2:
                        exists = True
                        break

        else:
            try:
                self.__executeSVN("proplist", "\"" + filename + "\"", split=True)
                exists = True
            except Process.ProcessException:
                pass

        return exists

    def getCommitMsg(self):
        """ Returns the commit message. """
        output = self.__executeSVN("info", split=True)
        temp = output[3:]
        msg = "".join(temp)
        return msg.strip()

    def getRevision(self):
        """ Returns the id of the revision or transaction. """
        return self.txnName

    def getProperty(self, keyword, filename):
        """ Returns a specified property of a file. """
        if not self.hasProperty(keyword, filename):
            raise PropertyNotFoundException(keyword, filename)
    
        return self.__executeSVN("propget", " ".join([keyword, "\"" + filename + "\""]))

    def hasProperty(self, keyword, filename):
        """ Checks if a given file has the given property. """
        return keyword in self.listProperties(filename)

    def listProperties(self, filename):
        """ Returns a list of names of the properties for a file."""
        if not self.fileExists(filename):
            raise FileNotFoundException(filename)

        return self.__executeSVN("proplist", "\"" + filename + "\"", split=True)
