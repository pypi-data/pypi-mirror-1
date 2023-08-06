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
__date__ = '$LastChangedDate: 2008-05-30 19:41:17 +0200 (Fri, 30 May 2008) $'
__version__ = '$Rev: 207 $'

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import Boolean
from sqlalchemy import Integer

from sqlalchemy.orm import mapper
from sqlalchemy.orm import relation

from aditam.server.model import meta

from aditam.server.model.report import Report

commands_table = Table('commands', meta.metadata,
        Column('id', Integer, primary_key=True),
        Column('label', Unicode(80), nullable=False),
        Column('command_line', Unicode(1024), nullable=False),
        )

class Command(object):
    """ """
    pass

mapper(Command, commands_table)

tasks_commands_table = Table('tasks_commands', meta.metadata,
        Column('id', Integer, primary_key=True),
        Column('command_id', Integer, ForeignKey('commands.id'),
            nullable=False),
        Column('task_id', Integer, ForeignKey('tasks.id'),
            nullable=False),
        Column('position', Integer(4), nullable=False),
        Column('logged', Boolean, default=True),
        Column('locking', Boolean, default=False),
        )

class CommandOrder(object):
    """ """
    pass

from aditam.server.model.task import Task

mapper(CommandOrder, tasks_commands_table,
        order_by=tasks_commands_table.c.position,
        properties=dict(
            command=relation(Command, backref='commands_order'),
            task=relation(Task, backref='commands_order')
            ),
        )

commands_reports_table = Table('commands_reports', meta.metadata,
        Column('id', Integer, primary_key=True),
        Column('command_id', Integer, ForeignKey('commands.id')),
        Column('report_id', Integer, ForeignKey('reports.id')),
        Column('stdout', UnicodeText),
        Column('stderr', UnicodeText),
        Column('result', Integer(4), nullable=False),
        )

class CommandReport(object):
    """ """
    pass

mapper(CommandReport, commands_reports_table,
        properties=dict(
            report=relation(Report, uselist=False, backref='command_reports'),
            command=relation(Command, uselist=False, backref='command_reports'),
            )
        )
