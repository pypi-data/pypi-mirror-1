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
import time

from threading import Thread, RLock
from Queue import Queue
from Queue import Empty
from datetime import datetime
from copy import copy

from aditam.server.loggers import netlogger
from aditam.core.agentjob import AgentJob
from aditam.core.model.farmnode import FarmNode
from aditam.core.model.meta import Session
from aditam.core.model.command import CommandOrder
from aditam.core.model.job import Job

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
        self.lock = RLock()
        self.agents = dict()
        self.agents_unreachable = dict()
        agents = Session.query(FarmNode).filter_by(state='up').all()
        if agents:
            for agent in agents:
                netlogger.debug("AgentPool : Add %s in the up list.", agent.name)
                self.add(agent.id, Queue())

        agents_unreachable = Session.query(FarmNode).filter_by(state='unreachable').all()
        if agents_unreachable:
            for agent in agents_unreachable:
                netlogger.debug("AgentPool : Add %s in the unreachable list.", agent.name)
                self.add(agent.id, Queue(), 'unreachable')

    def add_agent(self, id, name):
        """
        id : the farmnode id
        name : the name of the agent
        """
        self.add(id, Queue())
        if self.agents_unreachable.has_key(id):
            netlogger.info('Agent %s is back.' % (name))
            self.remove(id, 'unreachable')

    def add(self, id, agent_pool, state='up'):
        """
        add an agent from the pool
        """
        self.lock.acquire()
        try:
            if state == 'up':
                self.agents[id] = agent_pool
            if state == 'unreachable':
                self.agents_unreachable[id] = agent_pool
        finally:
                self.lock.release()

    def remove(self, id, state=None):
        """
        remove an agent from the pool
        state : up or down. If the state is not
        define all the agent will be removed
        """
        self.lock.acquire()
        try:
            if state == 'up' or not state:
                if self.agents.has_key(id):
                    del self.agents[id]
            if state == 'unreachable' or not state:
                if self.agents_unreachable.has_key(id):
                    del self.agents_unreachable[id]
        finally:
                self.lock.release()

    def up(self, id):
        """
        Signal that an agent is up
        """
        self.lock.acquire()
        try:
            id = int(id)
            farmnode = Session.query(FarmNode).get(id)
            if self.agents_unreachable.has_key(id):
                netlogger.info('Agent %s is back.' % (farmnode.name))
            farmnode.state = "up"
            farmnode.last_up_date = datetime.now()
            if self.agents_unreachable.has_key(id):
                self.add(id, self.agents_unreachable[id])
                self.remove(id, 'unreachable')
            if not self.agents.has_key(id):
                self.add(id, Queue())
            Session.update(farmnode)
            Session.commit()
        finally:
            self.lock.release()
        

    def assign_job(self, job, farmnode_id):
        """
        This method assign a job to a farmnode
        True: OK
        False: Failed
        """
        self.lock.acquire()
        try:
            farmnode = Session.query(FarmNode).get(farmnode_id)
            job.farmnode = farmnode
            job.status = "running"
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

            if self.agents.has_key(farmnode_id):
                self.agents[farmnode_id].put(agentjob)
                Session.update(job)
                Session.commit()
                return True
            else:
                netlogger.warning("Assign job : agent %s not found." % (farmnode.name))
                return False
        finally:
            self.lock.release()

    def get_job(self, agent_id):
        """
        This return the agentjob asign to the agent_id
        return None if no job have been assigned.
        """
        self.lock.acquire()
        try:
            if self.agents.has_key(agent_id):
                return self.agents[agent_id].get_nowait()
            else:
                netlogger.warning("AgentPool::get_job : agent %s not found." % (agent_id))
        except Empty:
            return None
        finally:
            self.lock.release()

    def get_agents(self, state="up"):
        """
        return a list of up agents
        state : up or down
        """
        if state == 'up':
            return copy(self.agents)
        elif state == 'unreachable':
            return copy(self.agents_unreachable)

