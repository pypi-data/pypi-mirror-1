# pylint: disable-msg=W0231

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

""" Execute a Process and return the output. """

import subprocess

class ProcessException(Exception):
    def __init__(self, command, exitCode, output):
        self.command = command
        self.output = output
        self.exitCode = exitCode

    def __str__(self):
        return "Command '%s' exited with exitCode %s:\n%s" % (self.command, self.exitCode, self.output)

    def __repr__(self):
        return self.__str__()


def execute(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
        return output
    else:
        raise ProcessException(command, exitCode, output)
