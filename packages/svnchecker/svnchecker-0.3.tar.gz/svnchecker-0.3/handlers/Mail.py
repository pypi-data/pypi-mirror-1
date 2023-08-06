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

""" Send the message as E-Mail. """

import smtplib
import socket
import datetime


class MailHandler:
    def __init__(self, transaction, config, check, msg):
        """ Main function. """
        self.transaction = transaction
        self.config = config
        self.check = check
        self.msg = msg

    def getLogSubject(self):
        fromID = self.transaction.getUserID()
        return "SVN update by %s at %s" % (fromID, datetime.datetime.now().strftime("%H:%M - %d.%m.%Y"))

    def getErrorSubject(self):
        fromID = self.transaction.getUserID()
        return "Checkin error by '%s' in check '%s'" % (fromID, self.check)

    def getLogAddresses(self):
        return self.config.getArray("%s.SuccessAddresses" % self.check)
        
    def getErrorAddresses(self):
        return self.config.getArray("%s.FailureAddresses" % self.check)
    
    def createMail(self, fromAddress, toAddress, subject, content):
        """ Creates the content of the mail. """
        return ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (fromAddress, toAddress, subject)) + content

    def sendMail(self, subject, toAddresses):
        """ Actually send the message. """
        fromAddress = self.transaction.getUserID() + "@" + socket.gethostname()
        server = smtplib.SMTP('localhost')
        server.set_debuglevel(0)
        for toAddress in toAddresses:
            mail = self.createMail(fromAddress, toAddress, subject, self.msg)
            server.sendmail(fromAddress, toAddress, mail)
        server.quit()


def run(transaction, config, check, msg, exitCode):
    handler = MailHandler(transaction, config, check, msg)

    if exitCode == 0:
        subject = handler.getLogSubject()
        addresses = handler.getLogAddresses()
    else:
        subject = handler.getErrorSubject()
        addresses = handler.getErrorAddresses()

    handler.sendMail(subject, addresses)
