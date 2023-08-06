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
__date__ = '$LastChangedDate: 2008-06-01 12:47:47 +0200 (Sun, 01 Jun 2008) $'
__version__ = '$Rev: 217 $'

from datetime import datetime

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Unicode
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import UnicodeText

from sqlalchemy.orm import mapper
from sqlalchemy.orm import relation

from aditam.server.model import meta

jobs_table = Table('jobs', meta.metadata,
        Column('id', Integer, primary_key=True),
        Column('execute_date', DateTime, nullable=False),
        Column('status', String(30), nullable=False),
        Column('task_id', Integer, ForeignKey('tasks.id'), nullable=False),
        Column('farmnode_id', Integer, ForeignKey('farmnodes.id'),
            default=None),
        Column('user_id', Integer, ForeignKey('users.id')),
        Column('report_id', Integer, ForeignKey('reports.id'), unique=True)
        )

class Job(object):
    """ Job database object """

    def get_commands(self):
        """ return a list with the commands """
        commands = list()
        if self.task:
            for command_order in self.task.commands_order:
                commands.append(command_order.command)
        return commands
        
from aditam.server.model.task import Task
from aditam.server.model.farmnode import FarmNode
from aditam.server.model.user import User
from aditam.server.model.report import Report

mapper(Job, jobs_table,
        properties=dict(
            task=relation(Task, backref='jobs'),
            farmnode=relation(FarmNode, backref='job'),
            launcher=relation(User, backref='jobs'),
            report=relation(Report, backref='jobs')
            )
        )
