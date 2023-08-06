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

__author__ = '$LastChangedBy: jschneider $'
__date__ = '$LastChangedDate: 2008-06-01 21:09:01 +0200 (Sun, 01 Jun 2008) $'
__version__ = '$Rev: 223 $'

import logging
import time
import Pyro.core

from threading import Thread
from Pyro.errors import ConnectionClosedError

class Monitoring(Thread):
    def __init__(self, host, port, hostname):
        """ """
        Thread.__init__(self)
        self.server = Pyro.core.getProxyForURI("PYROLOC://%s:%s/server" % \
            (host, port))
        self.hostname = hostname

    def run(self):
        """
        Launch the loop
        """
        logging.debug("Starting the monitoring ...")
        while 1:
            try:
                self.server.agent_up(self.hostname)
            except ConnectionClosedError, e:
                # TODO : try to reconnect
                logging.error(e)
                raise SystemExit(e)
            time.sleep(6)
 
