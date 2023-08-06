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
import shutil
import os

from setuptools import setup, find_packages
from ConfigParser import ConfigParser

# Project uses reStructuredText, so ensure that the docutils get
# installed or upgraded on the target machine
install_requires = [
    "setuptools >= 0.6c7",
    "SQLAlchemy >= 0.4, < 0.5.0beta"
]

README = open(os.path.join(os.path.dirname(__file__),
    'README.txt')).read()

def update_conf(old, sample):
    """
    Add the new changes in the configuration
    """
    print "Update your configuration : %s" % old
    conf = ConfigParser()
    conf.readfp(open(old))
    sample_conf = ConfigParser()
    sample_conf.readfp(open(sample))
    for section in sample_conf.sections():
        if not conf.has_section(section):
            conf.add_section(section)
        for option in sample_conf.options(section):
            if not conf.has_option(section, option):
                conf.set(section, option, sample_conf.get(section, option))
    conf.write(open(old, 'w'))

def main():
    if len(sys.argv) <= 1:
        sys.argv.append('-h')
    elif sys.argv[1].startswith('install') or sys.argv[1].startswith('develop'):
        conf_path = os.path.join(os.path.dirname(__file__),
                'aditam', 'core', 'conf')
        server = os.path.join(conf_path, 'aditam-server.conf')
        agent = os.path.join(conf_path, 'aditam-agent.conf')
        if os.path.isfile(server):
            update_conf(server, server+"-sample")
        else:
            shutil.copy(server+"-sample", server)
        if os.path.isfile(agent):
            update_conf(agent, agent+"-sample")
        else:
            shutil.copy(agent+"-sample", agent)

if __name__ == "__main__":
    main()

setup(
    name = "aditam.core",
    version = "0.1",
    include_package_data=True,
    install_requires = install_requires,
    zip_safe = False,
    scripts = ['aditam-admin.py'],


    package_data = {
        '': ['conf/*.conf'],
    },
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
    long_description = README,
    url = "http://www.aditam.org/",
    test_suite = 'nose.collector'
)

