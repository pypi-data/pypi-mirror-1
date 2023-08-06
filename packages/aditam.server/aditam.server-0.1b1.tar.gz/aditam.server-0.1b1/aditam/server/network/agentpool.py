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
import datetime
from threading import Thread
from Queue import Queue
from Queue import Empty
import time

from datetime import datetime
from aditam.core.agentjob import AgentJob
from aditam.server.model.farmnode import FarmNode
from aditam.server.model.meta import Session
from aditam.server.network.server import Daemon
from aditam.server.loggers import netlogger
from aditam.server.model.command import CommandOrder
from aditam.server.model.job import Job

class AgentPool:
    """
    This class stock a list of agents
    An agent is dictionnary with keys :
    id, ip, port and agent (Pyro agent object)
    """

    def __init__(self):
        """
        Launch the Pyro daemon
        """
        self.agents = dict()
        agents = Session.query(FarmNode).filter_by(state='up').all()
        if agents:
            for agent in agents:
                netlogger.debug("AgentPool : Add %s in the up list.", agent.name)
                self.agents[agent.id] = Queue()

        self.agents_unreachable = dict()
        agents_unreachable = Session.query(FarmNode).filter_by(state='unreachable').all()
        if agents_unreachable:
            for agent in agents_unreachable:
                netlogger.debug("AgentPool : Add %s in the unreachable list.", agent.name)
                self.agents_unreachable[agent.id] = Queue()

        daemon = Daemon(self)
        daemon.start()

    def add_agent(self, id):
        """
        id : the farmnode id
        """
        id = int(id)
        farmnode = Session.query(FarmNode).get(id)
        netlogger.info('New agent %s.' % (farmnode.name))
        farmnode.state = "up"
        farmnode.last_up_date = datetime.now()
        self.agents[id] = Queue()
        if self.agents_unreachable.has_key(id):
            self.remove(id, 'unreachable')
        Session.update(farmnode)
        Session.commit()

    def remove(self, id, state=None):
        """
        remove an agent from the pool
        state : up or down. If the state is not
        define all the agent will be removed
        """
        if state == 'up' or not state:
            if self.agents.has_key(id):
                del self.agents[id]
        if state == 'unreachable' or not state:
            if self.agents_unreachable.has_key(id):
                del self.agents_unreachable[id]

    def assign_job(self, job, farmnode_id):
        """
        This method assign a job to a farmnode
        """
        farmnode = Session.query(FarmNode).get(farmnode_id)
        job.farmnode = farmnode
        Session.update(job)
        Session.commit()
        agentjob = AgentJob(job_id=job.id)

        # Add the job's commands in the agentjob obj
        commands = list()
        commands_order = Session.query(CommandOrder).filter_by(task_id=job.task.id).all()
        for command_order in commands_order:
            command = command_order.command
            cmd = {'id': command.id,
                    'job_id': job.id,
                    'command_line': command.command_line}
            commands.append(cmd)
        agentjob.set_commands(commands)

        # TODO : search if the agents is in the unreachable agents dict
        if self.agents.has_key(farmnode_id):
            self.agents[farmnode_id].put(agentjob)
        else:
            netlogger.warning("Assign job : agent %s not found." % (farmnode.name))

    def get_job(self, agent_id):
        """
        This return the agentjob asign to the agent_id
        return None if no job have been assigned.
        """
        try:
            if self.agents.has_key(agent_id):
                return self.agents[agent_id].get_nowait()
            else:
                netlogger.warning("AgentPool::get_job : agent %s not found." % (agent_id))
        except Empty:
            return None

    def get_agents(self, state="up"):
        """
        return a list of up agents
        state : up or down
        """
        if state == 'up':
            return self.agents
        elif state == 'unreachable':
            return self.agents_unreachable
