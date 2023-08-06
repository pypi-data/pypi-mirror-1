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
__date__ = '$LastChangedDate: 2008-05-20 13:51:02 +0200 (Tue, 20 May 2008) $'
__version__ = '$Rev: 171 $'

from threading import Thread
import time
from datetime import datetime
#from database import session, metadata, get_engine
from aditam.server.model.meta import Session
from aditam.server.model.job import Job
from aditam.server.loggers import cronlogger
from sqlalchemy import and_

class Crontab(Thread):
    """ Crontab class: this class fetch tasks and transmit them to the manager """
    def __init__ (self, jobpool):
       """ init of the crontab """
       Thread.__init__(self)
       self.jobpool = jobpool
       self.refresh = 15 # todo recupererr la conf depuis le ficheir de conf
       self.lastrefresh = datetime.today()
    
    def __loop(self):
        """ crontab routine """
        while 1:
            cronlogger.debug("getting new tasks ...")
            now = datetime.today()
            jobs = list()
            jobs = Session.query(Job).filter(
                    and_(Job.execute_date>=self.lastrefresh, Job.execute_date<now)
                    ).all()
            self.lastrefresh = now
            if jobs:
                for job in jobs:
                    cronlogger.debug("New job : %s", job.id)
                    self.jobpool.add_job(job.id)
            # faire la query entre self.lastrefresh et now
            # puis remplir la liste et la donner a jerome
            time.sleep(self.refresh)

    def run(self):
        """ run the crontab """
        cronlogger.debug("Starting crontab ...")
        self.__loop()

