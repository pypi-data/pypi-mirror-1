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

""" Checkout files from the repository to file system locations. """

import shutil

def run(transaction, config):

    entries = config.getArray("Checkout.Entries")
    
    for entry in entries:

        source = config.getString("Checkout.%s.Source" % entry)
        destination = config.getString("Checkout.%s.Destination" % entry)

        if transaction.fileExists(source):
            filepath = transaction.getFile(source)
        else:
            return ("File %r to checkout does not exist in the repository." % source, 1)

        try:
            shutil.move(filepath, destination)
        except IOError, e:
            return ("Failed to checkout file %r to %r: %s" % (source, destination, e), 1)

    return ("", 0)
