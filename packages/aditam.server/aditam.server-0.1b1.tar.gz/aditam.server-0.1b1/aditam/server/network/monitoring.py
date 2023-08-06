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
__date__ = '$LastChangedDate: 2008-06-01 21:06:48 +0200 (Sun, 01 Jun 2008) $'
__version__ = '$Rev: 222 $'

import Pyro.core
import time

from threading import Thread
from datetime import datetime
from datetime import timedelta

from aditam.server.model.farmnode import FarmNode
from aditam.server.model.job import Job
from aditam.server.model.meta import Session
from aditam.core.error import NotRespondingError
from aditam.server.loggers import netlogger

from aditam.server.config import srv_config
from aditam.core.error import ConfigError

class Monitoring(Thread):
    """
    This check the agents state
    """

    def __init__(self, agentpool):
        """
        agentpool : AgentPool object
        """
        Thread.__init__(self)
        self.agentpool = agentpool

    def run(self):
        """ This will launch a loop """
        netlogger.debug("Launch monitoring")
        while 1:
            self.check_agents()
            # TODO : this value must be settable
            time.sleep(5)

    def _find_farmnodes(self, job):
        """ return a list of serevrs which can execute your job """
        servers = list()
        commands = job.get_commands()
        for farmnode in Session.query(FarmNode):
            ok = True
            for command in commands:
                if not command in farmnode.commands:
                    ok = False
                    break
            if ok:
                servers.append(farmnode)
        return servers

        
    def select_agent(self, job_id):
        """
        Select the best agent to excute our task.
        return the id of the agent
        """
        job = Session.query(Job).get(job_id)
        farmnodes = self._find_farmnodes(job)
        if not len(farmnodes):
            netlogger.warning("No farm node avaliable for task %s (job %d)" % \
            (job.task.label, job.id))
        # TODO make something smarter
        for id, agent in self.agentpool.get_agents().iteritems():
            agent_farmnode = Session.query(FarmNode).get(id)
            active_jobs = Session.query(Job).filter(Job.farmnode_id!=None).all()
            for farmnode in farmnodes:
                if agent_farmnode.id == farmnode.id:
                    for active_job in active_jobs:
                        if active_job.farmnode_id == id:
                            return None
                    return id
        return None

    def _check_up_agents(self):
        """
        This will check if the agents with up state are up.
        If the agent doesn't reply it state will change to unreachable.
        """
        agents = self.agentpool.get_agents()
        agents_down = self.agentpool.get_agents('unreachable')
        down_ids = list()
        for id, agent in agents.iteritems():
            if not srv_config.has_option("timeout", "agent_timeout"):
                netlogger.error("No agent timeout set in the config file")
                raise ConfigError, "No agent timeout set in the config file"
            timeout = srv_config.getint("timeout", "agent_timeout")
            farmnode = Session.query(FarmNode).get(id)
            if (datetime.now() - timedelta(seconds=timeout)) > \
                    farmnode.last_up_date:
                        netlogger.warning('Agent %s is unreachable !' % \
                                (farmnode.name))
                        farmnode.unreachable_date = datetime.now()
                        farmnode.state = "unreachable"
                        agents_down[id] = agent
                        Session.update(farmnode)
                        Session.commit()
                        down_ids.append(id)
        for id in down_ids:
            self.agentpool.remove(id, 'up')

    def _check_unreachable_agents(self):
        """
        This will check if the agents with unreachable state are up.
        """
        agents = self.agentpool.get_agents()
        agents_down = self.agentpool.get_agents('unreachable')
        up_ids = list()
        for id, agent in agents_down.iteritems():
            timeout = srv_config.getint("timeout", "agent_timeout")
            if not timeout:
                netlogger.error("No agent timeout set in the config file")
                raise ConfigError, "No agent timeout set in the config file"
            farmnode = Session.query(FarmNode).get(id)
            if (datetime.now() - timedelta(seconds=timeout)) <= \
                    farmnode.last_up_date:
                netlogger.info("Agent %s is back.", farmnode.name)
                farmnode.state = "up"
                agents[id] = agent
                up_ids.append(id)
                Session.update(farmnode)
                Session.commit()
        for id in up_ids:
            self.agentpool.remove(id, 'unreachable')

    def check_agents(self):
        """ Check if the agents is up """
        netlogger.debug("Check the agents.")
        self._check_up_agents()
        self._check_unreachable_agents()

