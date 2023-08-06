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
__date__ = '$LastChangedDate: 2008-05-30 19:41:17 +0200 (Fri, 30 May 2008) $'
__version__ = '$Rev: 207 $'

"""
Create and populate the database
"""

import aditam.server
from datetime import datetime
from datetime import timedelta
from aditam.server.model.meta import metadata, Session, engine
from aditam.server.model.user import User
from aditam.server.model.group import Group
from aditam.server.model.permission import Permission
from aditam.server.model.job import Job
from aditam.server.model.command import Command, CommandOrder
from aditam.server.model.task import Task
from aditam.server.model.farmnode import FarmNode
from aditam.server.model.report import Report

class Bootstrap:

    def create_tables(self):
        """ Create the database's tables """
        from aditam.server.model import meta
        meta.metadata.create_all(bind=meta.engine)

    def create_admin(self):
        """ This will create the user admin """
        g1 = None
        if not Session.query(Group).filter_by(group_name=u'admin').first():
            g1 = Group()
            g1.group_name = u'admin'
            Session.save(g1)
        if not g1:
            g1 = Session.query(Group).filter_by(group_name=u'admin').first()
        if not Session.query(User).filter_by(login=u'admin').first():
            u1 = User()
            u1.login = u'admin'
            u1.password = u'admin'
            u1.email_address = 'john.doe@example.com'
            u1.firstname = u'John'
            u1.lastname = u'Doe'
            u1.level = 50
            u1.lang = "en"
            g1.users.append(u1)
            Session.save(u1)
        if not Session.query(Permission).filter_by(permission_name=u'administrate').first():
            p1 = Permission()
            p1.permission_name = u"administrate"
            p1.groups.append(g1)
            Session.save(p1)
        Session.commit()
    
    def create_commands(self):
        """
        Create examples commands
        """
        if not Session.query(Command).filter_by(label=u'List current directory on Unix / Linux').first():
            cmd1 = Command()
            cmd1.command_line=u"ls"
            cmd1.label = u"List current directory on Unix / Linux"
            Session.save(cmd1)
        if not Session.query(Command).filter_by(label=u'List current directory on Windows').first():
            cmd2 = Command()
            cmd2.command_line=u"dir"
            cmd2.label = u"List current directory on Windows"
            Session.save(cmd2)
        Session.commit()

