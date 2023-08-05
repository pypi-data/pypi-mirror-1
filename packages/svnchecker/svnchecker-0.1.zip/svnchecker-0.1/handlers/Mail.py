#!/usr/bin/python
#----------------------------------------------------------------------------
# svnchecker - Mail.py
#
# Send the message per Mail
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

"""Send the message per Mail"""

import smtplib
import datetime

class Handler:
    """Handler Class"""
    
    def main(self, transaction, config, module, msg, exitCode):
        """Main Function"""
        self.transaction = transaction
        self.config = config
        self.module = module
        self.msg = msg
        self.exitCode = exitCode
        
        if exitCode == 0:
            self.sendLogMessage()
        else:
            self.sendErrorMessage()
            
    def sendLogMessage(self):
        """Send a Log message"""
        subject = "SVN update: %s" % datetime.datetime.now().strftime("%H:%M - %d.%m.%Y")
        addresses = self.config.getArray("%s.SuccessAddresses" % self.module)
        self.__sendMail(subject, self.msg, addresses)
    
    def sendErrorMessage(self):
        """Send an Error message"""
        fromID = self.transaction.getUserID()
        subject = "Checkin error by '%s' in module '%s'" % (fromID, self.module)
        addresses = self.config.getArray("%s.FailureAddresses" % self.module)
        self.__sendMail(subject, self.msg, addresses)

    def __getUserMail(self):
        """Return the user Mail address of the current transaction"""
        id = self.transaction.getUserID()

        try:
            email = self.config.getString("Mail.%s" % id)
        except:
            email = self.config.getString("Mail.default")
            
        return email

    def __sendMail(self, subject, msg, toAddresses):
        """Actually send the message"""
        fromAddress = self.__getUserMail()
        server = smtplib.SMTP('localhost')
        server.set_debuglevel(0)
        for address in toAddresses:
            mail_msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
                % (fromAddress, address, subject)) + msg
    
            server.sendmail(fromAddress, address, mail_msg)
        server.quit()
        