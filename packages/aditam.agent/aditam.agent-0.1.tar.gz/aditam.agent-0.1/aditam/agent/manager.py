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

import Pyro.core
import Pyro.naming
import Pyro.util
import Pyro.errors
import platform
import sys
import socket
import logging
import time

from aditam.agent.jobmanager import JobManager
from aditam.agent.monitoring import Monitoring
from aditam.core.config import agent_config
from aditam.core.errors import ConfigError

class Manager:

    def __check_config(self):
        """Test if the agent configuration is full"""
        try:
            agent_config.need_section('server')
            agent_config.need_option('server', 'host')
            agent_config.need_section('logger')
            agent_config.need_option('logger', 'level')
            agent_config.need_option('logger', 'filename')
        except ConfigError, e:
            logging.critical(e)
            raise SystemExit, e

    def __init_logger(self):
        """Set the default logger of the agent"""
        level = agent_config.get('logger', 'level')
        if level == "DEBUG":
            level = logging.DEBUG
        elif level == "WARNING":
            level = logging.WARNING
        elif level == "ERROR":
            level = logging.ERROR
        elif level == "CRITICAL":
            level = logging.CRITICAL
        else:
            level = logging.INFO
        filename = agent_config.get('logger', 'filename')
        logging.basicConfig(level=level,
                format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                filename=filename,
                filemode='a'
                )
        # define a Handler which writes messages to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(level)
        formatter = logging.Formatter("%(levelname)-8s %(message)s")
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def __get_uri(self, host, port, obj_name):
        """ """
        if not host:
            host = agent_config.get('server', 'host')
        if not host:
            err = "No host define ! Please use aditam-admin.py -a or " +\
                    "aditam-agent.py --host"
            logging.critical(err)
            raise SystemExit, err
        if not port and agent_config.has_option('server', 'port'):
            port = agent_config.get('server', 'port')
        if not port:
            return 'PYROLOC://' + host + '/' + obj_name
        else:
            return 'PYROLOC://' + host + ':'+ port + '/' + obj_name

    def start(self, host=None, port=0):
        """Launch the agent"""
        self.__check_config()
        self.__init_logger()
        os = platform.system()
        # initialize the client
        Pyro.core.initClient()
        uri_server = self.__get_uri(host, port, 'server')
        uri_feedback = self.__get_uri(host, port, 'feedback')
        server = Pyro.core.getAttrProxyForURI(uri_server)

        if agent_config.has_option('agent', 'hostname') and\
                agent_config.get('agent', 'hostname'):
            hostname = agent_config.get('agent', 'hostname')
        else:
            hostname = socket.getfqdn()

        try:
            server.add_agent(unicode(hostname), os)
        except Pyro.errors.ProtocolError,x:
            logging.critical("Server is unreachable : %s" % x)
            raise SystemExit, x
        jobmanager = JobManager(uri_server, uri_feedback, hostname)
        jobmanager.start()
        monitoring = Monitoring(uri_server, hostname)
        monitoring.start()
        logging.info('Agent is started.')
        while 42:
            try:
                time.sleep(42)
            except KeyboardInterrupt:
                logging.info("Keyboard interruption")
                self.stop()

    def stop(self):
        """
        Stop the farmnode
        """
        logging.info("Stop Aditam agent")
        sys.exit(0)

