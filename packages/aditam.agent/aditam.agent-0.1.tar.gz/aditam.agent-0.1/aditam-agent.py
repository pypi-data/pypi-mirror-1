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
__date__ = '$LastChangedDate: 2008-06-01 21:09:01 +0200 (Sun, 01 Jun 2008) $'
__version__ = '$Rev: 223 $'

import os
import sys

from optparse import OptionParser

from aditam.agent.manager import Manager
from aditam.core.config import agent_config

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
                stderr=agent_config.get("logger", "filename"),
                pidfile="/var/run/aditam-agent.pid",
                )
        if daemon.service(parser):
            (options, args) = (daemon.options, daemon.args)
            manager = Manager()
            manager.start(options.host, options.port)
    else:
        (options, args) = parser.parse_args()
        manager = Manager()
        manager.start(options.host, options.port)

if __name__ == "__main__":
    main()
