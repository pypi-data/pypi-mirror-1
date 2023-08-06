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

import Pyro.core

from datetime import datetime

from aditam.server.loggers import netlogger
from aditam.server.model.meta import Session
from aditam.server.model.job import Job
from aditam.server.model.farmnode import FarmNode
from aditam.server.model.command import CommandReport

class FeedBack(Pyro.core.ObjBase):
    """ Manage the feedback of the tasks """

    def add_command_report(self, agentreport, job_id):
        """
        The agent will send a report by task
        """
        netlogger.debug("STDOUT : %s" % (agentreport['stdout']))
        netlogger.debug("STDERR : %s" % (agentreport['stderr']))
        netlogger.debug("RETURN CODE : %s" % (agentreport['result']))
        job = Session.query(Job).get(job_id)
        netlogger.debug("Command %d for job %s is finished." % \
                (agentreport['cmd_id'], job.task.label))
        report = job.report
        command_report = CommandReport()
        command_report.stdout = agentreport['stdout']
        command_report.stderr = agentreport['stderr']
        command_report.result = agentreport['result']
        command_report.report = report
        command_report.command_id = agentreport['cmd_id']
        Session.save(command_report)
        Session.commit()

    def end_job(self, job_id, success=True):
        """
        The agent agent call this method when the task is finished
        job_id : the job id
        """
        job = Session.query(Job).get(job_id)
        if success:
            netlogger.info("The task %s (job : %d) have finished successfully." % \
                    (job.task.label, job.id))
        else:
            netlogger.warning("The task %s (job : %d) have failled." % \
                    (job.task.label, job.id))
        report = job.report
        report.end_date = datetime.now()
        report.success = success
        job.status = "ended"
        job.farmnode = None
        Session.update(report)
        Session.update(job)
        Session.flush()
        Session.commit()
