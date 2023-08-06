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
__date__ = '$LastChangedDate: 2008-05-23 21:31:46 +0200 (Fri, 23 May 2008) $'
__version__ = '$Rev: 182 $'

"""
This class is used by the agent
"""


class AgentJob:
    """ Light job objects for the agent """

    def __init__(self, commands=list(), job_id=None):
        """
        commands : list of commands
        """
        self._commands = commands
        self._job_id = job_id

    def get_commands(self):
        """
        return a list with the commands dictionnaries.
        A command is a dictionnary : {'id': x, 'job_id': y, 'name': 'foo'}
        """
        return self._commands

    def set_commands(self, commands):
        """
        commands : list of command
        A command is a dictionnary with the id and the command line
        """
        # TODO : control commands ??
        self._commands = commands

    def get_job_id(self):
        """ return the job_id """
        return self._job_id

    def set_job_id(self, job_id):
        """ set the job id """
        self._job_id = job_id

