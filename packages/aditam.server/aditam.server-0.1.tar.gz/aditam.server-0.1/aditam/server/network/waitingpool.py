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

__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$Rev$'

import time

from threading import Thread
from Queue import Queue
from aditam.server.loggers import netlogger

class WaitingPool(Thread):
    """
    Manage the jobs that are wiating for a free agent
    """

    def __init__(self, jobpool):
        """ """
        Thread.__init__(self)
        self.jobs = Queue()
        self.jobpool = jobpool

    def add_job(self, job_id):
        """
        Add a new job in the waiting pool
        """
        netlogger.info("Put job %d in the waiting queue" % job_id)
        self.jobs.put(job_id)

    def run(self):
        """ """
        while 1:
            job_id = self.jobs.get()
            time.sleep(10)
            self.jobpool.treat_job(job_id)

