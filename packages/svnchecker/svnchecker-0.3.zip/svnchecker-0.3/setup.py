#!/usr/bin/env python

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

# Documentation for distutils: http://docs.python.org/dist/dist.html

from distutils.core import setup

setup(name='svnchecker',
      version='0.3',
      description='SVNChecker is a framework for Subversion hook scripts.',
      long_description='SVNChecker is a framework for Subversion pre-commit hooks in order to implement checks of the to be commited files before they are commited. For example, you can check for the code style or unit tests. The output of the checks can be send by mail or be written into a file or simply print to the console..',
      author='Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)',
      author_email='Heinrich.Wendel@dlr.de',
      maintainer='Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)',
      maintainer_email='Andreas.Schreiber@dlr.de',
      url='http://svnchecker.tigris.org',
      packages = ['checks', 'handlers', 'modules'],
      scripts=['Main.py'],    
      data_files=[('config', ['svncheckerconfig.ini'])],  
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Bug Tracking',
          'Topic :: Software Development :: Version Control',
          ],
     )