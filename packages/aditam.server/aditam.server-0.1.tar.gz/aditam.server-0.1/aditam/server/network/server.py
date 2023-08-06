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

"""
Manage the Pyro server
"""

import Pyro.core
import Pyro.naming
import Pyro

from Pyro.errors import NamingError
from threading import Thread, RLock
from datetime import datetime

from aditam.core.errors import AditamError
from aditam.core.config import srv_config
from aditam.core.model.farmnode import FarmNode
from aditam.core.model.meta import Session
from aditam.server.loggers import netlogger
from aditam.server.network.feedback import FeedBack

class Server(Pyro.core.ObjBase):
    """ This class is used by the agents """

    def __init__(self, agentpool):
        """ """
        Pyro.core.ObjBase.__init__(self)
        self.agentpool = agentpool
        self.lock = RLock()

    def add_agent(self, agent_name, os):
        """ add the agent in the agent pool """
        agent_name = unicode(agent_name)
        self.lock.acquire()
        try:
            farmnode = Session.query(FarmNode).filter_by(name=agent_name).first()
            if not farmnode:
                netlogger.info("Add new agent : %s. OS : %s." % (agent_name, os))
                farmnode = FarmNode()
                farmnode.name = unicode(agent_name)
                Session.save(farmnode)
            farmnode.last_up_date = datetime.now()
            farmnode.state = "up"
            Session.update(farmnode)
            Session.commit()
        finally:
            self.lock.release()
        self.agentpool.add_agent(farmnode.id, farmnode.name)
        return None

    def disable_agent(self, agent_name):
        """
        Delete an agent in the server
        """
        self.lock.acquire()
        try:
            farmnode = Session.query(FarmNode).filter_by(name=agent_name).first()
            if not farmnode:
                netlogger.error("Agent %s not found", agent_name)
            else:
                farmnode.state = "down"
                Session.update(farmnode)
                Session.commit()
        finally:
            self.lock.release()

    def agent_up(self, agent_name):
        """
        Tail the server that your agent is up.
        """
        agent_name = unicode(agent_name)
        self.lock.acquire()
        try:
            netlogger.debug("Agent %s is up.", agent_name)
            farmnode = Session.query(FarmNode).filter_by(name=agent_name).first()
            if farmnode:
                self.agentpool.up(farmnode.id)
            else:
                netlogger.warning("Unkmow agent name : %s." % agent_name)
        finally:
            self.lock.release()

    def get_job(self, agent_name):
        """
        return an AgentJob if the agent have a job to do.
        return None if the agent have nothing to do.
        """
        self.agent_up(agent_name)
        agent_name = unicode(agent_name)
        self.lock.acquire()
        try:
            netlogger.debug("%s asks a job." % agent_name)
            farmnode = Session.query(FarmNode).filter_by(name=agent_name).first()
            if farmnode:
                farmnode.last_up_date = datetime.now()
                Session.update(farmnode)
                Session.commit()
                job = self.agentpool.get_job(farmnode.id)
                if job:
                    netlogger.info("New job for %s" % (agent_name))
                return job
            else:
                netlogger.warning("Unkmow agent name : %s." % agent_name)
        finally:
            self.lock.release()
        return None


class Daemon(Thread):
    """ Launch the Pyro daemon in a thread """

    def __init__(self, agentpool, host=None, port=0):
        """
        """
        Thread.__init__(self)
        Pyro.config.PYRO_MAXCONNECTIONS = 400
        self.agentpool = agentpool
        if srv_config.has_section('network'):
            if srv_config.has_option('network', 'port') and not port:
                port = srv_config.getint('network', 'port')
            if srv_config.has_option('network', 'host') and not host:
                host = srv_config.get('network', 'host')
        self.port = port
        self.host = host
        self.daemon = None

    def run(self):
        """ launch the Pyro server """
        # initialize the server and set the default namespace group
        Pyro.core.initServer()

        self.daemon = Pyro.core.Daemon(port=self.port, host=self.host)

        self.daemon.connect(Server(self.agentpool),"server")
        self.daemon.connect(FeedBack(),"feedback")

        netlogger.info("The daemon runs on %s:%d" %
                (self.daemon.hostname, self.daemon.port))
        self.daemon.requestLoop()

    def shutdown(self):
        """ Shutdown the Pyro daemon """
        if self.daemon:
            netlogger.debug("Shutdown Pyro daemon")
            self.daemon.shutdown()


