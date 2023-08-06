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
__date__ = '$LastChangedDate: 2008-06-01 21:06:48 +0200 (Sun, 01 Jun 2008) $'
__version__ = '$Rev: 222 $'

import time
from Queue import Queue
from Queue import Empty
from threading import Thread, RLock
from datetime import datetime

from aditam.server.loggers import netlogger
from aditam.server.network.monitoring import Monitoring
from aditam.server.network.waitingpool import WaitingPool
from aditam.core.errors import AditamError
from aditam.core.config import srv_config
from aditam.core.model.farmnode import FarmNode
from aditam.core.model.meta import Session
from aditam.core.model.job import Job
from aditam.core.model.report import Report

class JobPool(Thread):
    """ Put the jobs in queue and send them to the AgentPool """

    def __init__(self, agentpool):
        """
        Inialize monitoring, agentpool and daemon class
        Reput job in queue
        """
        Thread.__init__(self)
        self.jobs = Queue()
        self.lock = RLock()
        self.agentpool = agentpool
        self.monitoring = Monitoring(self.agentpool)
        self.waitingpool = WaitingPool(self)
        self.monitoring.start()
        self.waitingpool.start()
        # reput in queue jobs
        queue_jobs = Session.query(Job).filter_by(status='queue').all()
        for job in queue_jobs:
            netlogger.info('Reput in queue task : %s', job.task.label)
            self.jobs.put(job.id)

    def __job_timeout(self, job, timeout=None, timeout_base="seconds"):
        """
        test and treat a job timeout
        timeout_base: seconds, minutes or hours
        Return True if the job is timeout and False in the other case
        """
        if timeout:
            delta = datetime.now() - job.execute_date
            if timeout_base == "minutes":
                timeout *= 60
            if timeout_base == "hours":
                timeout *= 3600
            if delta.seconds > timeout:
                netlogger.error("Task %s timeout : no agent available" %
                        job.task.label)
                job.status = "ended"
                report = Report()
                report.success = False
                job.report = report
                Session.save(report)
                Session.update(job)
                Session.commit()
                return True
        return False

    def treat_job(self, job_id):
        """
        Convert the job object to an AgentJob object, find an agent
        and send the job to this agent
        """
        Session.clear()
        job = Session.query(Job).get(job_id)
        if not job:
            netlogger.critical("Report this bug : JobPool::__treat_job no job\
            in the database.")
            raise AditamError, "No job %d in the Database" % job_id
        agent_id = self.monitoring.select_agent(job_id)
        if not agent_id:
            timeout = srv_config.getint('timeout', 'no_agent_for_task')
            if not self.__job_timeout(job, timeout, "hours"):
                self.waitingpool.add_job(job.id)
        else:
            report = Report()
            report.begin_date = datetime.now()
            Session.save(report)
            job.report = report
            Session.update(job)
            Session.commit()
            if not self.agentpool.assign_job(job, agent_id):
                self.waitingpool.add_job(job.id)
        return None

    def run(self):
        """
        A loop which treat jobs
        """
        netlogger.debug('Launch the Job poool')
        while 1:
            job_id = self.jobs.get()
            netlogger.debug("Jobpool NEW job job_id : %d", job_id)
            self.treat_job(job_id)

    def add_job(self, job_id):
        """
        job_id : id of the job object
        Put the job in a FIFO queue
        """
        netlogger.debug('New job %d in the pool' % job_id)
        job = Session.query(Job).get(job_id)
        job.status = 'queue'
        Session.update(job)
        Session.commit()
        self.jobs.put(job_id)

    def add_jobs(self, job_ids):
        """ job_ids : list of job ids """
        for job_id in job_ids:
            netlogger.debug('New job %d in the pool' % job_id)
            self.jobs.put(job_id)


