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
__date__ = '$LastChangedDate: 2008-05-20 13:51:02 +0200 (Tue, 20 May 2008) $'
__version__ = '$Rev: 171 $'

"""
The manager launch the programm
"""

from Queue import Queue
import sys
import time
import platform
import logging

from aditam.core.errors import ConfigError
from aditam.core.config import srv_config
from aditam.server.network.agentpool import AgentPool
from aditam.server.network.server import Daemon
from aditam.server.loggers import netlogger


class Manager:
    """ Global management of the aditam server """

    def __init__(self, host=None, port=0):
        """ """
        self.jobpool = None
        self.crontab = None
        self.daemon = None
        self.host = host
        self.port = port

    def check_config(self):
        """
        Check if the configuration is good.
        """
        try:
            srv_config.need_section('database')
            srv_config.need_option('database', 'dsn')
            srv_config.need_section('timeout')
            srv_config.need_option('timeout', 'agent_timeout')
            srv_config.need_option('timeout', 'no_agent_for_task')
            srv_config.need_section('logging')
            srv_config.need_option('logging', 'filename')
            srv_config.need_option('logging', 'level')
            srv_config.need_option('logging', 'crontab_level')
            srv_config.need_option('logging', 'network_level')
        except ConfigError, e:
            logging.critical(e)
            raise SystemExit, e

    def get_level(self, level_name):
        """ return a logging level (int) """
        res = logging.INFO
        if level_name == "DEBUG":
            res = logging.DEBUG
        elif level_name == "WARNING":
            res = logging.WARNING
        elif level_name == "ERROR":
            res = logging.ERROR
        elif level_name == "CRITICAL":
            res = logging.CRITICAL
        return res


    def _init_logging(self):
        """
        Set all the loggers level and format
        """
        level = self.get_level(srv_config.get('logging', 'level'))
        logging.basicConfig(level=level,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=srv_config.get('logging', 'filename'),
                    filemode='a')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('network').addHandler(console)
        logging.getLogger('crontab').addHandler(console)
        level = self.get_level(srv_config.get('logging', 'crontab_level'))
        logging.getLogger('network').setLevel(level)
        level = self.get_level(srv_config.get('logging', 'network_level'))
        logging.getLogger('crontab').setLevel(level)

    def start(self):
        """
        Start the ADITAM server.
        Launch a thread for the crontab and another one for the jobpool
        """
        self.check_config()
        netlogger.info("Starting aditam server")
        self._init_logging()
        # TODO : create all threads here
        from aditam.server.network.jobpool import JobPool
        from aditam.server.crontab.crontab import Crontab
        agentpool = AgentPool()
        self.jobpool = JobPool(agentpool)
        self.crontab = Crontab(self.jobpool)
        self.daemon = Daemon(agentpool, self.host, self.port)
        self.jobpool.start()
        self.crontab.start()
        self.daemon.start()
        # We need to keep the main thread to manage signals
        while 42:
            try:
                time.sleep(42)
            except KeyboardInterrupt:
                netlogger.info("Keyboard interruption.")
                self.stop()

    def stop(self):
        """
        Stop the ADITAM agent.
        """
        netlogger.info("Stopping aditam server")
        if self.daemon:
            self.daemon.shutdown()
        sys.exit(0)

