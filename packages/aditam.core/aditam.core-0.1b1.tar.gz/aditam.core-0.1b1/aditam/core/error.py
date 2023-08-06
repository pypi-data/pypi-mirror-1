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

__author__ = '$LastChangedBy: jschneider $'
__date__ = '$LastChangedDate: 2008-05-24 01:01:32 +0200 (Sat, 24 May 2008) $'
__version__ = '$Rev: 186 $'

"""
ADITAM's Exception classes
"""

import logging

class AditamError(Exception):
    """ Exception class for ADITAM """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ConfigError(AditamError):
    pass

class ContrabError(AditamError):
    pass

class ManagerError(AditamError):
    pass

class NotRespondingError(AditamError):
    """ Exception class for ADITAM """
    def __init__(self, value):
        self.value = value
