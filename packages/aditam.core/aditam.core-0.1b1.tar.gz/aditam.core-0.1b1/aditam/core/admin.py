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
__date__ = '$LastChangedDate: 2008-06-10 21:18:33 +0200 (mar, 10 jun 2008) $'
__version__ = '$Rev: 93 $'

import socket
from optparse import OptionParser

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

    def _get_param(self, question, default_value=None, nullable=True):
        """
        Ask on the command line a parameter.
        """
        param = None
        while not param:
            if default_value != None:
                print question, "[%s] " % default_value,
            else:
                print question,
            param = raw_input()
            if not param and default_value:
                return default_value
            if param or nullable:
                return param
            else:
                print "This can't be null !"

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
        
    def _get_dsn(self):
        """
        Ask the user the databases parameters to create the dsn
        """
        db_type, db_host, db_port, db_user, db_password = None, None, None, None, None
        db_drivers = ('sqlite', 'mysql', 'postgres', 'oracle', 'mssql', 'firebird')
        while db_type not in db_drivers:
            db_type = self._get_param("Datababe type ? (sqlite, mysql, postgres,"
                    " oracle, mssql, or firebird)")
            if db_type not in  db_drivers:
                print "Invalid database driver."
        self._test_driver(db_type)
        if db_type != "sqlite":
            db_name = self._get_param("Database name ?", nullable=False)
            db_host = self._get_param("Database address ?", "localhost")
            while db_port != '' and type(db_port) != type(int()):
                db_port = self._get_param("Database port ?", '')
                if db_port:
                    try:
                        db_port = int(db_port)
                    except ValueError:
                        print "Port must be an integer !"
            db_user = self._get_param("Database user ?")
            db_password = self._get_param("Database password ?")
            dsn = "%s://" % db_type
            if db_user:
                dsn += "%s:%s@" % (db_user, db_password)
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
        # TODO : Remove this test in the version 0.2
        try:
            from aditam.server.config import srv_config
        except ImportError:
            print "Sorry you must install aditam.server to configure the db."
            raise SystemExit

        dsn = self._get_dsn()
        srv_config.set('database', 'dsn', dsn)
        try:
            conf = open(srv_config.get_conf_path(), 'w')
        except IOError, e:
            print e
            raise SystemExit("Insufficient privileges !")
        srv_config.write(conf)
        conf.close()

    def createdb(self):
        """ Create the database tables """
        # TODO : Remove this test in the version 0.2
        try:
            from aditam.server.bootstrap import Bootstrap
        except ImportError:
            print "Sorry you must install aditam.server to create the db."
            raise SystemExit
        bootstrap = Bootstrap()
        bootstrap.create_tables()
        bootstrap.create_admin()
        bootstrap.create_commands()

    def config_server(self):
        """ Configure the server """
        try:
            from aditam.server.config import srv_config
            from aditam.server.config import logging_config
        except ImportError:
            print "Sorry you must install aditam.server to configure the server."
            raise SystemExit

        port = None
        host = self._get_param("Listen address or host ?", "0.0.0.0")
        while type(port) != type(int()):
            port = self._get_param("Listen port ?", 7766)
            try:
                port = int(port)
            except ValueError:
                print "Port must be an integer !"
        srv_config.set('network', 'host', host)
        srv_config.set('network', 'port', port)
        try:
            conf = open(srv_config.get_conf_path(), 'w')
        except IOError, e:
            print e
            raise SystemExit("Insufficient privileges !")
        srv_config.write(conf)
        conf.close()

        log_path = None
        while not log_path:
            log_path = self._get_param("Logging file path ?", "aditam.server.log")
            try:
                f = open(log_path, 'a')
            except IOError, e:
                print e
                log_path = None
        logging_config.set('handler_log', 'args', "('%s', 'a')" % log_path)
        log_level = None
        levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        while log_level not in levels:
            log_level = self._get_param("Logging level ? (DEBUG, INFO, WARNING,"
                    " ERROR OR CRITICAL)", "INFO")
            if log_level not in levels:
                print "Bad log level !"
        logging_config.set('logger_root', 'level', log_level)
        try:
            conf = open(logging_config.get_conf_path(), 'w')
        except IOError, e:
            print e
            raise SystemExit("Insufficient privileges !")
        logging_config.write(conf)
        conf.close()


    def config_agent(self):
        """ Configure the agent """
        try:
            from aditam.agent.config import agent_config
        except ImportError:
            print "Sorry you must install aditam.agent to configure the agent."
            raise SystemExit

        port = None
        host = self._get_param("Server address or host ?", "127.0.0.1")
        while type(port) != type(int()):
            port = self._get_param("Server port ?", 7766)
            try:
                port = int(port)
            except ValueError:
                print "Port must be an integer !"
        agent_config.set('server', 'host', host)
        agent_config.set('server', 'port', port)
        hostname = self._get_param("Agent hostname ?", socket.getfqdn())
        try:
            conf = open(agent_config.get_conf_path(), 'w')
        except IOError, e:
            print e
            raise SystemExit("Insufficient privileges !")
        agent_config.write(conf)
        conf.close()

