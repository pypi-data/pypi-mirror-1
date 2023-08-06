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

desc = """An Object Relation Mapper for XML"""
summ = """xmlobjects is a python library for pythonic building, parsing and manipulation of xml. xmlobjects is modeled primarily on common ORM libraries for python in that it tries to map a native python api feel to the building of xml structures."""

PACKAGE_NAME = "xmlobjects"
PACKAGE_VERSION = "0.4"

setup(name=PACKAGE_NAME,
      version=PACKAGE_VERSION,
      description=desc,
      summary=summ,
      author='Open Source Applications Foundation',
      author_email='tools-dev@osafoundation.org',
      url='http://code.google.com/p/xmlobjects/',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages=['xmlobjects'],
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

