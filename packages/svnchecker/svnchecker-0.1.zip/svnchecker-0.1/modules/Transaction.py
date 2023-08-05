#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - Transaction.py
#
# Class to work with transactions.
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

"""Class to work with transactions."""

import Process
import os
import re

class Transaction:

    def __init__(self, reposPath, txnName):
        """Initialize the transaction object"""
        try:
            dummy = int(txnName)
            self.type = "revision"
        except:
            self.type = "transaction"
            
        self.reposPath = reposPath
        self.txnName = txnName
        
        self.tmpdir = Process.execute("mktemp -d /tmp/tmp.XXXXXX")[0].strip()
        
    def __del__(self):
        Process.execute("rm -fR %s" % self.tmpdir)
    
    def __executeSVN(self, command, arg = ""):
        value = Process.execute("svnlook --%s %s %s %s %s" % (self.type, self.txnName, command, self.reposPath, arg))
        return value
    
    def getUserID(self):
        """Return the user ID of the current transaction"""
        user = self.__executeSVN("author")
        return user[0].strip()
    
    def getFiles(self, checkList = [".*"], ignoreList = []):
        """
        Return a map of all modified files
        
        Valid attributes are:
        A: Item added to repository
        D: Item delete from repository
        U: File contents changed
        _U: Properties of item changed
        UU: File content and properties changed
        """
        output = self.__executeSVN("changed")
        files = {}
        for file in output:
            status = file[0:3].strip()
            datei = file[4:].strip()
            if self.__check(datei, checkList) == True and self.__check(datei, ignoreList) == False:
                files[datei] = status
        return files
    
    def __check(self, datei, list):
        for ignore in list:
            regex = re.compile(ignore)
            if regex.search(datei):
                return True
        return False
    
    def getFile(self, filename):
        """Return path of a tempory copy of a file."""
        output = self.__executeSVN("cat", filename)
        msg = ""
        for line in output:
            msg += line
        Process.execute("mkdir -p %s" % os.path.join(self.tmpdir, os.path.dirname(filename)))
        fd = open(os.path.join(self.tmpdir, filename), "w")
        fd.write(msg)
        fd.close()
        return (os.path.join(self.tmpdir, filename))
        
    def fileExists(self, filename):
        """Returns whether a file exists or not."""
        try:
            self.__executeSVN("proplist", filename)
            return True
        except Process.ProcessException:
            return False
    
    def getCommitMsg(self):
        """Return the commit message"""
        output = self.__executeSVN("info")
        temp = output[3:]
        msg = ""
        for line in temp:
            msg += line
        return msg
    
    def getReposPath(self):
        """Return the path to the current repository"""
        return self.reposPath
    
    def getRevision(self):
        """Return the revision of the to be commited transaction"""
        return self.txnName
    
    def getKeyword(self, keyword, file):
        """Return the keywords of the files."""
        try:
            output = self.__executeSVN("propget", " ".join([keyword, file]))
            return output[0]
        except Process.ProcessException:
            return ""
            
