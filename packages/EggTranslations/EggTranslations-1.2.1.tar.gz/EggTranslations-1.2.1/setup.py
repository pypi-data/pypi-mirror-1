#!/bin/env python
# -*- coding: utf-8 -*-

#   Copyright (c) 2006-2009 Open Source Applications Foundation
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


def get_description():
    # Get our long description from the documentation
    f = file('README.txt')
    lines = []
    for line in f:
        if not line.strip():
            break     # skip to first blank line
    for line in f:
        if line.startswith('.. contents::'):
            break     # read to table of contents
        lines.append(line)
    f.close()
    return ''.join(lines)

setup(
    name="EggTranslations",
    version="1.2.1",
    classifiers=["Development Status :: 4 - Beta",
                 "Environment :: Console",
                 "Framework :: Chandler",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: Apache Software License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 "Topic :: Software Development :: Internationalization"],
    url="http://chandlerproject.org/Projects/EggTranslations",
    author="Brian Kirsch",
    author_email="bkirsch@osafoundation.org",
    maintainer="Grant Baillie",
    maintainer_email="grant@osafoundation.org",
    description="Provides an API for accessing localizations and resources packaged in python eggs",
    long_description=get_description(),
    license="Apache License, Version 2.0",
    test_suite="tests",
    py_modules=["egg_translations"],
    include_package_data=True,
    zip_safe=True,
)
