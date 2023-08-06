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

""" Checks python files for coding style. """

import StringIO

from pylint import lint
from pylint.reporters.text import TextReporter

def run(transaction, config):

    check = config.getArray("Pylint.CheckFiles", [".*\.py"])
    ignore = config.getArray("Pylint.IgnoreFiles", [])
    files = transaction.getFiles(check, ignore)

    config = config.getString("Pylint.ConfigFile", "")

    files = [transaction.getFile(oneFile[0]) for oneFile in files.iteritems() if oneFile[1] in ["A", "U", "UU"]]

    output = StringIO.StringIO()
    reporter = TextReporter(output)

    if config:
        lint.Run(["--rcfile=%s" % config, "--reports=n"] + files, reporter=reporter)
    else:
        lint.Run(["--reports=n"] + files, reporter=reporter)

    output = output.getvalue()

    if output:
        return (output, 1)
    else:
        return ("", 0)
