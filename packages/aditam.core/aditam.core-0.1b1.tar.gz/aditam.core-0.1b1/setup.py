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

from setuptools import setup, find_packages

# Project uses reStructuredText, so ensure that the docutils get
# installed or upgraded on the target machine
install_requires = [
    "setuptools>=0.6c2",
]


setup(
    name = "aditam.core",
    version = "0.1b1",
    include_package_data=True,
    install_requires = install_requires,
    scripts = ['aditam-admin'],
    zip_safe = False,

    packages = find_packages(),
    namespace_packages = ['aditam'],
    # metadata for upload to PyPI
    author = "ADITAM project",
    author_email = "contact@aditam.org",
    description = "Automated and DIstributed TAsk Manager core part.",
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
      long_description="""
=============
Aditam Core
=============

------------
Description
------------

ADITAM facilitates mass task managing over heterogeneous network.
The project is slipt in 5 parts :
 * adtitam.core (Python) : the common parts of the Aditam agent and server.
 * aditam.server (Python) : the server
 * aditam.agent (Python) : the agent

 * aditam clac (php) : a command line ui.
 * aditam gui (php) : the aditam website.

This package is the common part of the aditam packages and it contains a script to configure
the agent, the server and the database.
""",

    url = "http://www.aditam.org/",
    test_suite = 'nose.collector'
)

