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
__date__ = '$LastChangedDate: 2008-05-20 13:51:02 +0200 (Tue, 20 May 2008) $'
__version__ = '$Rev: 171 $'

from aditam.server import bootstrap
from aditam.server.network.agentpool import AgentPool
from aditam.server.model.meta import Session
from aditam.server.model.job import Job

class TestNetwork:

    def __init__(self):
        """ """
        bootstrap.launch()

    def test_find_farmnodes(self):
        """ """
        job = Session.query(Job).get(1)
        farmnodes = self._find_farmnodes(job)
        assert len(farmnodes) == 1
        assert farmnodes[0].name == "totosrv"

        job = Session.query(Job).get(2)
        farmnodes = self._find_farmnodes(job)
        assert len(farmnodes) == 0

    def test_agent_pool(self):
        """ this test the AgentPool """
        agentpool = AgentPool()
        #agentpool.daemon.stop()
        # Add totosrv
        agentpool.add_agent(1, '192.168.1.1', 3030, test_agent=False)
        # Add titisrv
        agentpool.add_agent(2, '192.168.1.1', 3030, test_agent=False)
        agents = agents.get_agents()
        agents_down = agents.get_agents('down')
        assert len(agents) == 2
        assert len(agents) == 0
        agentpool.remove(1, 'up')
        agents = agents.get_agents()
        agents_down = agents.get_agents('down')
        assert len(agents) == 1
        assert len(agents) == 1
        agentpool.remove(2, 'up')
        agents = agents.get_agents()
        agents_down = agents.get_agents('down')
        assert len(agents) == 0
        assert len(agents) == 2
        agentpool.remove(1, 'down')
        agentpool.remove(2, 'down')
        agents = agents.get_agents()
        agents_down = agents.get_agents('down')
        assert len(agents) == 0
        assert len(agents) == 0

