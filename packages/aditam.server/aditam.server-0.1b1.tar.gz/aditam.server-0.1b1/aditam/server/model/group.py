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

from datetime import datetime

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy.orm import mapper
from sqlalchemy.orm import relation

from aditam.server.model import meta
from aditam.server.model.user import User

groups_table = Table('groups', meta.metadata,
        Column('id', Integer, primary_key=True),
        Column('group_name', Unicode(50), unique=True, nullable=False),
        Column('created', DateTime, default=datetime.now),
        )

users_groups_table = Table('users_groups', meta.metadata,
        Column('user_id', Integer, ForeignKey('users.id',
            onupdate='CASCADE', ondelete='CASCADE')),
        Column('group_id', Integer, ForeignKey('groups.id',
            onupdate='CASCADE', ondelete='CASCADE'))
        )

class Group(object):
    """ """
    pass

mapper(Group, groups_table,
        properties=dict(
            users=relation(User,
                secondary=users_groups_table, backref='groups')
            )
        )
