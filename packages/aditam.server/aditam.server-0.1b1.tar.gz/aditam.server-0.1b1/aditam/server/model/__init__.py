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

import sqlalchemy as sa
from sqlalchemy import orm

from aditam.server.model import meta
from aditam.server.config import srv_config

def init_model(engine):
    """ Call me before using any of the tables or classes in the model. """

    sm = orm.sessionmaker(autoflush=True, transactional=True, bind=engine)

    meta.engine = engine
    meta.Session = orm.scoped_session(sm)

if not meta.Session:
    if not srv_config.get('database', 'dsn'):
        raise SystemExit("Please configure the database with the aditam-admin "
                "script or in the configuration file")
    dsn = srv_config.get('database', 'dsn')
    engine = sa.create_engine(dsn)
    init_model(engine)
    try:
        connection = engine.connect()
        connection.close()
    except sa.exceptions.OperationalError, e:
        print e
        raise SystemExit("Please configure your database using aditam-admin !")

