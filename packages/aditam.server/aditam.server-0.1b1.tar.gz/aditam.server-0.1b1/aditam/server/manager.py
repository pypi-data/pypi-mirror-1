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
import logging
import platform

from aditam.server.network.jobpool import JobPool
from aditam.server.crontab.crontab import Crontab


class Manager:
    """ Global management of the aditam server """

    def __init__(self):
        """ """
        self.jobpool = None
        self.crontab = None

    def start(self):
        """
        Start the ADITAM server.
        Launch a thread for the crontab and another one for the jobpool
        """
        logging.info("Starting aditam server")
        self.jobpool = JobPool()
        self.crontab = Crontab(self.jobpool)
        self.jobpool.start()
        self.crontab.start()
        
    def stop(self):
        """
        Stop the ADITAM agent.
        """
        logging.info("Stopping aditam server")
        raise SystemExit("Goodbye !")
        
