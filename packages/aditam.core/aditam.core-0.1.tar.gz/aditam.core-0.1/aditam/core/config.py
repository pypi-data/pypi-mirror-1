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
__date__ = '$LastChangedDate: 2008-05-24 01:01:32 +0200 (Sat, 24 May 2008) $'
__version__ = '$Rev: 186 $'

"""
Manage all config files
"""

import os
import shutil

from pkg_resources import resource_filename

from ConfigParser import ConfigParser
from aditam.core.errors import ConfigError

def get_conf_path(conf_name, conf_dirs):
    """ return the first valid conf path """
    for conf_dir in conf_dirs:
        conf_path = os.path.join(conf_dir, conf_name)
        if os.path.isfile(conf_path):
            return conf_path
    raise ConfigError, "Configuration file %s not found" % conf_name


class Config(ConfigParser):
    """
    Generic Config class
    """

    instance = None
    conf_path = None

    def __new__(cls, *args, **kargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, *args, **kargs)
        return cls.instance

    def __init__(self, conf_name, conf_dirs):
        """
        Load the default config
        conf_name: the configuration file name (example : aditam-server.conf)
        conf_dirs: the possible directory of the configuration file
        """
        ConfigParser.__init__(self)
        try:
            conf_path = get_conf_path(conf_name, conf_dirs)
        except ConfigError:
            conf_path = resource_filename("aditam.core", os.path.join("conf", conf_name))
        self.conf_path = conf_path
        self.readfp(open(conf_path))

    def get_conf_path(self):
        """
        Return the path of the config file
        """
        return self.conf_path

    def need_section(self, section):
        """
        If the section doesn't exist this will
        raise an ConfigError exception
        section: section name
        """
        if not self.has_section(section):
            err = "Bad configuration : no section %s" % section
            raise ConfigError, err

    def need_option(self, section, option):
        """
        If the option doesn't exist this will
        raise an ConfigError exception
        section: section name
        option: option name
        """
        if not self.has_option(section, option):
            err = "Bad configuration : no option %s in section %s" %\
                    (option, section)
            raise ConfigError, err


server_conf_name = "aditam-server.conf"
logging_conf_name = "aditam-logging.conf"
agent_conf_name = "aditam-agent.conf"
conf_dirs = [".",
        os.path.join(os.path.expanduser("~"), ".aditam"),
        "C:\Program Files\Aditam",
        "/etc",
        "/etc/aditam"]

srv_config = Config(server_conf_name, conf_dirs)
agent_config = Config(agent_conf_name, conf_dirs)

