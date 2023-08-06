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
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Time

from sqlalchemy.orm import mapper

from aditam.server.model import meta

reports_table = Table('reports', meta.metadata,
        Column('id', Integer, primary_key=True),
        Column('begin_date', DateTime),
        Column('end_date', DateTime),
        Column('success', Boolean, default=None),
        )

class Report(object):
    """ """
    pass

mapper(Report, reports_table)

