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

___author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$Rev$'

from aditam.core.admin import Admin

def main():
    """ """
    admin = Admin()
    admin.parse_line()

if __name__ == "__main__":
    main()

