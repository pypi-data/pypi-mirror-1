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

___author__ = '$LastChangedBy: schnei_e@EPITECH.NET $'
__date__ = '$LastChangedDate: 2008-10-20 22:25:59 +0200 (lun 20 oct 2008) $'
__version__ = '$Rev: 228 $'

import socket

from optparse import OptionParser
from aditam.core.errors import AditamError
from aditam.core.config import srv_config
from aditam.core.config import agent_config

class Admin:
    """
    Manage the aditam-admin's script.
    """

    def __init__(self):
        """ """
        self.parser = OptionParser()
        self.parser.add_option("-C", "--config-db",
                          action="store_true",
                          dest="configdb",
                          default=False,
                          help="Configure the database.")
        self.parser.add_option("-c", "--create-db",
                          action="store_true",
                          dest="createdb",
                          default=False,
                          help="Create the database tables and add the default data.")
        self.parser.add_option("-s", "--server",
                          action="store_true",
                          dest="server",
                          default=False,
                          help="Configure the server.")
        self.parser.add_option("-a", "--agent",
                          action="store_true",
                          dest="agent",
                          default=False,
                          help="Configure the agent (Server host and port)")

    def parse_line(self):
        """
        Parse the command line
        """
        (options, args) = self.parser.parse_args()
        if options.configdb:
            self.configdb()
        if options.createdb:
            self.createdb()
        if options.server:
            self.config_server()
        if options.agent:
            self.config_agent()

    def _get_param(self, question, default_value=None, nullable=True,
            allowed_values=None, param_type="string"):
        """
        Ask on the command line a parameter.
        param_type: int or string
        """
        param = None
        error = True
        while error:
            error = False
            if default_value != None:
                print question, "[%s]" % default_value,
            else:
                print question,
            param = raw_input()
            if not param and default_value:
                return default_value
            if not param and nullable and not allowed_values:
                return ''
            elif not param and not allowed_values:
                print "This can't be null"
                error = True
            if param_type == "int":
                try:
                    param = int(param)
                except ValueError:
                    print "Bad parameter type. %s is needed" % param_type
                    error = True
            if allowed_values and param in allowed_values:
                return param
            elif allowed_values:
                print "%s not allowed." % (param)
                error = True
        return param

    def _test_driver(self, db_type):
        """
        Test if the module is install
        """
        if db_type == "mysql":
            try:
                import MySQLdb
            except ImportError:
                raise SystemExit("Install MySQL-python module.")
        elif db_type == "postgres":
            try:
                import psycopg2
            except ImportError:
                raise SystemExit("Install psycopg2 module.")
        # TODO test the other databases

    def __get_log_path(self, default):
        """
        Ask to the user the path of the log file
        """
        log_path = None
        while not log_path:
            log_path = self._get_param("Logging file path ?", default)
            try:
                f = open(log_path, 'a')
            except IOError, e:
                print e
                log_path = None
        return log_path

    def _save_config(self, config_obj):
        """
        Write the new config file
        """
        try:
            conf = open(config_obj.get_conf_path(), 'w')
        except IOError, e:
            print e
            raise SystemExit("Insufficient privileges !")
        config_obj.write(conf)
        conf.close()

    def _get_dsn(self):
        """
        Ask the user the databases parameters to create the dsn
        """
        db_type, db_host, db_port, db_user, db_password = None, None, None, None, None
        db_drivers = ('sqlite', 'mysql', 'postgres', 'oracle', 'mssql', 'firebird')
        db_type = self._get_param("Datababe type ? (sqlite, mysql, postgres,"
                " oracle, mssql, or firebird)", allowed_values=db_drivers)
        self._test_driver(db_type)
        if db_type != "sqlite":
            db_name = self._get_param("Database name ?", nullable=False)
            db_host = self._get_param("Database address ?", "localhost")
            db_port = self._get_param("Database port ?", '', param_type='int')
            db_user = self._get_param("Database user ?")
            db_password = self._get_param("Database password ?")
            dsn = "%s://" % db_type
            if db_user and db_password:
                dsn += "%s:%s@" % (db_user, db_password)
            elif db_user:
                dsn += "%s@" % db_user
            dsn += db_host
            if db_port:
                dsn += ":%d" % db_port
            dsn += "/"
            dsn += db_name
        else:
            db_path = self._get_param("Database path ?", nullable=False)
            dsn = "%s:///%s" % (db_type, db_path)
        return dsn

    def configdb(self):
        """ Configure the database engine """
        dsn = self._get_dsn()
        srv_config.set('database', 'dsn', dsn)
        self._save_config(srv_config)

    def createdb(self):
        """ Create the database tables """
        from aditam.core.bootstrap import Bootstrap
        bootstrap = Bootstrap()
        bootstrap.create_tables()
        bootstrap.create_admin()
        bootstrap.create_commands()

    def config_server(self):
        """ Configure the server """
        host = self._get_param("Listen address or host ?", "0.0.0.0")
        port = self._get_param("Listen port ?", 7766, param_type='int')
        srv_config.set('network', 'host', host)
        srv_config.set('network', 'port', port)
        agent_timeout = self._get_param("Agent timeout ? (in seconds)", 30,
                param_type="int")
        srv_config.set('timeout', 'agent_timeout', agent_timeout)
        log_path = self.__get_log_path("aditam-server.log")
        srv_config.set('logging', 'filename', log_path)
        levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_level = self._get_param("Logging level ? (DEBUG, INFO, WARNING,"
                " ERROR OR CRITICAL)", "INFO", allowed_values=levels)
        srv_config.set('logging', 'level', log_level)
        srv_config.set('logging', 'crontab_level', log_level)
        srv_config.set('logging', 'network_level', log_level)
        self._save_config(srv_config)

    def config_agent(self):
        """ Configure the agent """
        host = self._get_param("Server hostname or ip ?", nullable=False)
        port = self._get_param("Server port ?", 7766, param_type='int')
        agent_config.set('server', 'host', host)
        agent_config.set('server', 'port', port)
        hostname = self._get_param("Agent hostname ?", socket.getfqdn())
        agent_config.set('agent', 'hostname', hostname)
        levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_level = self._get_param("Logging level ? (DEBUG, INFO, WARNING,"
                " ERROR OR CRITICAL)", "INFO", allowed_values=levels)
        agent_config.set('logger', 'level', log_level)

        log_path = self.__get_log_path("aditam-agent.log")
        agent_config.set('logger', 'filename', log_path)
        self._save_config(agent_config)

