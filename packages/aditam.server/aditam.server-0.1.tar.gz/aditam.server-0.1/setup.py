#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright (c) 2008 ADITAM project (contact@aditam.org)
#    License: GNU GPLv3
#
#    This file is part of the ADITAM project.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.  See the GNU General Public License
#    for more details.
#

___author__ = '$LastChangedBy: jschneider $'
__date__ = '$LastChangedDate: 2008-05-31 10:34:49 +0200 (Sat, 31 May 2008) $'
__version__ = '$Rev: 211 $'

import sys
import os

from setuptools import setup, find_packages

# Project uses reStructuredText, so ensure that the docutils get
# installed or upgraded on the target machine
install_requires = [
    "Pyro >= 0.7",
    "aditam.core >= 0.1",
    "setuptools >= 0.6c7"
]

README = open(os.path.join(os.path.dirname(__file__),
    'README.txt')).read()

setup(
    name = "aditam.server",
    version = "0.1",
    include_package_data=True,
    install_requires = install_requires,
    scripts = ['aditam-server.py'],
    zip_safe = False,

    packages = find_packages(),
    namespace_packages = ['aditam'],

    # metadata for upload to PyPI
    author = "ADITAM project",
    author_email = "contact@aditam.org",
    description = "Automated and DIstributed TAsk Manager server part.",
    license = "GPLv3",
    keywords = "tasks",
    classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Environment :: Console",
          "Intended Audience :: System Administrators",
          "Intended Audience :: Other Audience",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          ],
    long_description=README,
    url = "http://www.aditam.org/",
    test_suite = 'nose.collector'
)

