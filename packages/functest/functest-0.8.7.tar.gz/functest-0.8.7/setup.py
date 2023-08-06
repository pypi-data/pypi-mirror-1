#   Copyright (c) 2007 Mikeal Rogers
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from setuptools import setup, find_packages
import sys, os

desc = 'Functional test framework.'

summary = """Functest is a test tool/framework for testing in python.

It focuses on strong debugging, zero boiler plate, setup/teardown module hierarchies, and distributed result reporting"""

PACKAGE_NAME = "functest"
PACKAGE_VERSION = "0.8.7"

setup(name=PACKAGE_NAME,
      version=PACKAGE_VERSION,
      description=desc,
      long_description=summary,
      author='Mikeal Rogers',
      author_email='mikeal.rogers@gmail.com',
      url='http://code.google.com/p/functest/',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages=find_packages(),
      entry_points="""
            [console_scripts]
            functest = functest.bin:cli
          """,
      platforms =['Any'],                         
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                  ],
     )

