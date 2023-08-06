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

permissions_table = Table('permissions', meta.metadata,
        Column('id', Integer, primary_key=True),
        Column('permission_name', Unicode(16), unique=True),
        )

groups_permissions_table = Table('groups_permissions', meta.metadata,
        Column('group_id', Integer, ForeignKey('groups.id',
            onupdate='CASCADE', ondelete='CASCADE')),
        Column('permission_id', Integer, ForeignKey('permissions.id',
            onupdate='CASCADE', ondelete='CASCADE'))
        )

users_permissions_table = Table('users_permissions', meta.metadata,
        Column('user_id', Integer, ForeignKey('users.id',
            onupdate='CASCADE', ondelete='CASCADE')),
        Column('permission_id', Integer, ForeignKey('permissions.id',
            onupdate='CASCADE', ondelete='CASCADE'))
        )

tasks_permissions_table = Table('tasks_permissions', meta.metadata,
        Column('task_id', Integer, ForeignKey('tasks.id',
            onupdate='CASCADE', ondelete='CASCADE')),
        Column('permission_id', Integer, ForeignKey('permissions.id',
            onupdate='CASCADE', ondelete='CASCADE'))
        )

class Permission(object):
    """ """
    pass

from aditam.server.model.group import Group
from aditam.server.model.user import User
from aditam.server.model.task import Task

mapper(Permission, permissions_table,
        properties=dict(
            groups=relation(Group,
                secondary=groups_permissions_table, backref='permissions'),
            users=relation(User,
                secondary=users_permissions_table, backref='permissions'),
            tasks=relation(Task,
                secondary=tasks_permissions_table, backref='permissions')
            )
        )

