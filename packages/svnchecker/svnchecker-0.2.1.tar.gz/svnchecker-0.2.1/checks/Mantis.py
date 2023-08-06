# pylint: disable-msg=W0612

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

"""
Checks if a log message contains one or more valid MANTIS ID,
with a MANTIS ID <#> that is set to status 'in_progress' and
handled by the correct user.
"""

from modules import Mantis
import re

def run(transaction, config):

    mantis = Mantis.Mantis(config)

    logMessage = transaction.getCommitMsg()
    pattern = re.compile('MANTIS([:#]|[\s\-_]ID) ([0-9]+)')
    result = pattern.findall(logMessage)

    checkInProgress = config.getBoolean("Mantis.CheckInProgress", True)
    checkHandler = config.getBoolean("Mantis.CheckHandler", True)

    if len(result) == 0:
        msg = "Invalid log message: The message must contain 'MANTIS ID <#>'!"
        return (msg, 1)

    msg = ""
    exitCode = 0

    for (splitter, issueId) in result:
        if not mantis.issueExists(issueId):
            msg = "MANTIS ID %s not found!" % issueId
            exitCode = 1
            break

        if checkInProgress:
            status = mantis.issueGetStatus(issueId)
            if status != "in_progress":
                msg = "MANTIS ID %s is not 'in_progress'!" % issueId
                exitCode = 1
                break

        if checkHandler:
            user = transaction.getUserID()
            handler = mantis.issueGetHandler(issueId)

            if (user != handler):
                msg = "You are not the handler of MANTIS ID %s!" % issueId
                exitCode = 1
                break

    return (msg, exitCode)
