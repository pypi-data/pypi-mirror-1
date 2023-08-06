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

"""
User table, class and mapper
"""

import sha
from datetime import datetime

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy import Integer
from sqlalchemy import DateTime

from sqlalchemy.orm import mapper

from aditam.server.model import meta

users_table = Table('users', meta.metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('login', Unicode(30), nullable=False, unique=True),
        Column('password', String(40)),
        Column('email_address', String(100), nullable=False),
        Column('firstname', Unicode(50), nullable=False),
        Column('lastname', Unicode(50), nullable=False),
        Column('level', Integer(4), nullable=False),
        Column('lang', String(5), nullable=False),
        Column('created', DateTime, default=datetime.now),
        )

class User(object):
    """
    This class manage database users.
    """

    def _set_password(self, password):
        """
        encrypts password on the fly using the sha1
        algo
        """
        password = sha.new(password)
        self._password = password.hexdigest()

    def _get_password(self):
        """ returns the hash's password """
        return self._password

    password = property(_get_password, _set_password)

    def permissions(self):
        perms = set()
        for g in self.groups:
            perms |= set(g.permissions)
        return perms

    permissions = property(permissions)

mapper(User, users_table,
        properties=dict(
            _password=users_table.c.password
            )
        )
