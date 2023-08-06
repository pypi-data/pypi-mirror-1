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
from threading import Thread
from datetime import datetime

from aditam.server.loggers import netlogger
from aditam.server.network.agentpool import AgentPool
from aditam.server.network.monitoring import Monitoring
from aditam.server.model.farmnode import FarmNode
from aditam.server.model.meta import Session
from aditam.server.model.job import Job
from aditam.server.model.report import Report

class JobPool(Thread):
    """ Put the jobs in queue and send them to the AgentPool """

    def __init__(self):
        """
        Inialize monitoring and agentpool class
        """
        Thread.__init__(self)
        self.jobs = Queue()
        self.agentpool = AgentPool()
        self.monitoring = Monitoring(self.agentpool)
        try:
            self.monitoring.start()
        except KeyboardInterrupt:
            raise SystemExit

    def __treat_job(self, job_id):
        """
        Convert the job object to an AgentJob object, find an agent
        and send the job to this agent
        """
        job = Session.query(Job).get(job_id)
        agent_id = self.monitoring.select_agent(job_id)
        if not agent_id:
            netlogger.warning("No agent avaliable for task %s (job %d)" % \
                        (job.task.label, job.id))
            netlogger.warning("Reput this job in the queue")
            self.jobs.put(job_id)
        else:
            report = Report()
            report.begin_date = datetime.now()
            job.report = report
            job.status = "running"
            Session.save(report)
            Session.update(job)
            Session.commit()
            self.monitoring.check_agents()
            self.agentpool.assign_job(job, agent_id)
        return None


    def run(self):
        """
        A loop which treat jobs
        """
        netlogger.debug('Launch the Job poool')
        while 1:
            job_id = self.jobs.get()
            self.__treat_job(job_id)
            time.sleep(3)

    def add_job(self, job_id):
        """
        job_id : id of the job object
        Put the job in a FIFO queue
        """
        netlogger.debug('New job %d in the pool' % job_id)
        self.jobs.put(job_id)

    def add_jobs(self, job_ids):
        """ job_ids : list of job ids """
        for job_id in job_ids:
            netlogger.debug('New job %d in the pool' % job_id)
            self.jobs.put(job_id)


