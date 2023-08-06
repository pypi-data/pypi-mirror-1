# pylint: disable-msg=W0613, W0612

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

""" Append the message to one or more Mantis issues as note and update the SVNRevision field. """

from modules.Mantis import Mantis

import re

def run(transaction, config, check, msg, exitCode):

    mantis = Mantis(config)

    pattern = re.compile('MANTIS([:#]|[\s\-_]ID) ([0-9]+)')
    result = pattern.findall(msg)

    for (splitter, issueId) in result:
        if mantis.issueExists(issueId):
            mantis.issueAddNote(issueId, msg)
            mantis.issueSetCustomFieldIfExists(issueId, "SVNRevision", transaction.getRevision())
