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

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import UnicodeText

from sqlalchemy.orm import mapper
from sqlalchemy.orm import relation

from aditam.server.model import meta

farmnodes_table = Table('farmnodes', meta.metadata,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(60), nullable=False, unique=True),
        Column('description', UnicodeText, default=None),
        Column('ip', String(20)),
        Column('state', String(20), default="down", nullable=False),
        Column('last_up_date', DateTime, default=None),
        Column('OS', Unicode(50)),
        )

commands_farmnodes_table = Table('commands_farmnodes', meta.metadata,
        Column('command_id', Integer, ForeignKey('commands.id',
            onupdate='CASCADE', ondelete='CASCADE')),
        Column('farmnode_id', Integer, ForeignKey('farmnodes.id',
            onupdate='CASCADE', ondelete='CASCADE'))
        )

class FarmNode(object):
    """ """
    pass

from aditam.server.model.command import Command

mapper(FarmNode, farmnodes_table,
        properties=dict(
            commands=relation(Command,
                secondary=commands_farmnodes_table, backref='farmnodes'),
            )
        )
