# pylint: disable-msg=W0704

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

""" Create a log message. """

import datetime

def run(transaction, config):

    files = transaction.getFiles()

    msg = "Date: " + datetime.datetime.now().strftime("%H:%M - %d.%m.%Y") + "\n"
    msg += "Author: " + transaction.getUserID() + "\n"
    msg += "Revision: " + transaction.getRevision() + "\n\n"

    viewVcUrl = config.getString("Log.ViewVcUrl", "")
    if viewVcUrl:
        viewVcUrl += "&view=rev&revision=" + transaction.getRevision()
        msg += viewVcUrl + "\n\n"

    msg += "Modified Files:\n"
    for filename, attribute in files.iteritems():
        msg += "%s\t%s\n" % (attribute, filename)

    msg += "\n"

    msg += "Log Message:\n"
    msg += transaction.getCommitMsg()
    msg += "\n"

    return (msg, 0)
    