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
from threading import Thread
from datetime import datetime

from aditam.server.loggers import netlogger
from aditam.server.config import srv_config
from aditam.server.network.feedback import FeedBack
from aditam.server.model.farmnode import FarmNode
from aditam.server.model.meta import Session

class Server(Pyro.core.ObjBase):
    """ This class is used by the agents """

    def __init__(self, agentpool):
        """ """
        Pyro.core.ObjBase.__init__(self)
        self.agentpool = agentpool

    def add_agent(self, agent_name, os):
        """ add the agent in the agent pool """
        agent_name = unicode(agent_name)
        farmnode = Session.query(FarmNode).filter_by(name=agent_name).first()
        if not farmnode:
            netlogger.info("Add new agent : %s. OS : %s." % (agent_name, os))
            farmnode = FarmNode()
            farmnode.name = unicode(agent_name)
            farmnode.last_up_date = datetime.now()
            Session.save(farmnode)
            Session.commit()
        self.agentpool.add_agent(farmnode.id)
        return None

    def del_agent(self, agent_name):
        """
        Delete an agent in the server
        """
        # TODO : code this method
        pass

    def agent_up(self, agent_name):
        """
        Tail the server that your agent is up.
        """
        agent_name = unicode(agent_name)
        netlogger.debug("Agent %s is up.", agent_name)
        farmnode = Session.query(FarmNode).filter_by(name=agent_name).first()
        if farmnode:
            farmnode.last_up_date = datetime.now()
            Session.update(farmnode)
            Session.commit()
        else:
            netlogger.warning("Unkmow agent name : %s." % agent_name)

    def get_job(self, agent_name):
        """
        return an AgentJob if the agent have a job to do.
        return None if the agent have nothing to do.
        """
        agent_name = unicode(agent_name)
        netlogger.debug("%s asks a job." % agent_name)
        farmnode = Session.query(FarmNode).filter_by(name=agent_name).first()
        if farmnode:
            farmnode.last_up_date = datetime.now()
            Session.update(farmnode)
            Session.commit()
            job = self.agentpool.get_job(farmnode.id)
            if job:
                netlogger.info("New job %s for %s" % (job, agent_name))
            return job
        else:
            netlogger.warning("Unkmow agent name : %s." % agent_name)
        return None
        

class Daemon(Thread):
    """ Launch the Pyro daemon in a thread """

    def __init__(self, agentpool):
        """
        """
        Thread.__init__(self)
        self.agentpool = agentpool

    def run(self):
        """ launch the Pyro server """
        Pyro.core.initServer()
        host = None
        port = None
        if srv_config.has_section('network'):
            host = srv_config.get('network', 'host')
            port = srv_config.getint('network', 'port')
        daemon = Pyro.core.Daemon(host=host, port=port)
        uri = daemon.connectPersistent(Server(self.agentpool),"server")
        uri = daemon.connectPersistent(FeedBack(),"feedback")
        netlogger.info("The daemon runs on port:%d" % daemon.port)
        daemon.requestLoop()

