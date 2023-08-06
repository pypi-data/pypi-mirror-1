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

""" Check access rights on files. """

def run(transaction, config):

    rules = config.getArray("AccessRights.Rules")
    failure = []
    
    for rule in rules:

        check = config.getArray("AccessRights.%s.CheckFiles" % rule, [".*"])
        ignore = config.getArray("AccessRights.%s.IgnoreFiles" % rule, [])
        files = transaction.getFiles(check, ignore)
    
        allows = config.getArray("AccessRights.%s.AllowUsers" % rule, [])
        denies = config.getArray("AccessRights.%s.DenyUsers" % rule, [])

        for filename in files.keys():
            if allows and transaction.getUserID() not in allows:
                failure.append(filename)
            if denies and transaction.getUserID() in denies:
                failure.append(filename)
  
    if failure:
        msg = "You don't have rights to edit these files: \n"
        msg += "\n".join(failure)
        return (msg, 1)

    return ("", 0)
