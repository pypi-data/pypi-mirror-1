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
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy import Integer
from sqlalchemy import UnicodeText

from sqlalchemy.orm import mapper
from sqlalchemy.orm import relation

from aditam.server.model import meta

tasks_table = Table('tasks', meta.metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey('users.id')),
        Column('label', Unicode(100), nullable=False),
        Column('description', UnicodeText),
        Column('icon', Unicode(300)),
        )

class Task(object):
    """ """
    pass

from aditam.server.model.user import User
from aditam.server.model.command import CommandOrder

mapper(Task, tasks_table,
        properties=dict(
            creator=relation(User, backref='tasks'),
            )
        )
