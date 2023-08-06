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

import os
import re
import sys

from optparse import OptionParser

from aditam.server.manager import Manager
from aditam.core.config import srv_config

parser = OptionParser()

parser.add_option("-p", "--port",
        dest="port",
        metavar="<port>",
        help="Listen port",
        type="int")
parser.add_option("-H", "--host",
        dest="host",
        metavar="<host>",
        help="Listen host",
        type="string")

def main():
    if os.name == 'posix':
        from aditam.core.daemon import Daemon
        daemon = Daemon(
                stderr=srv_config.get("logging", "filename"),
                pidfile="/var/run/aditam-server.pid",
                )
        if daemon.service(parser):
            (options, args) = (daemon.options, daemon.args)
            manager = Manager(options.host, options.port)
            manager.start()
    else:
        (options, args) = parser.parse_args()
        manager = Manager(options.host, options.port)
        manager.start()

if __name__ == "__main__":
    main()

