#!/usr/bin/env python
#
#   Copyright (c) 2006-2007 Open Source Applications Foundation
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

from setuptools import setup

desc = """Simple WebDAV client."""
summ = """davclient is a simple WebDAV client that uses httplib.

>>> client = davclient.DAVClient('http://www.davsite.com:8080')
>>> client.set_basic_auth('user', 'pass')
>>> client.mkcol('/home/user/newcoll')
>>> client.put('/home/user/newcoll/blah.txt', body='sometext')
>>> assert client.response.status == 201
>>> client.get('/home/user/newcoll/blah.txt')
>>> assert client.response.body == 'sometext'"""

PACKAGE_NAME = "davclient"
PACKAGE_VERSION = "0.2.0"

setup(name=PACKAGE_NAME,
      version=PACKAGE_VERSION,
      description=desc,
      summary=summ,
      author='Open Source Applications Foundation',
      author_email='tools-dev@osafoundation.org',
      url='http://wiki.osafoundation.org/Projects/Davclient',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages=[PACKAGE_NAME],
      package_dir = {'':'src'},
      platforms =['Any'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                  ]
     )

