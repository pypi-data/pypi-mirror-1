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

__author__ = '$LastChangedBy: schnei_e@EPITECH.NET $'
__date__ = '$LastChangedDate: 2008-10-10 23:28:05 +0200 (ven 10 oct 2008) $'
__version__ = '$Rev: 188 $'

import logging
import time
import sys
import Pyro.errors

from aditam.core.config import agent_config

"""
Common function for the agent
"""

def autoreconnect(obj, method_call, *method_vars):
    """
    If the server is down the agent try to reconnect
    indefinitely.
    obj: pyro object
    Example :
    obj.foo("bar1", "bar2") => autoreconnect(obj, obj.foo, "bar1", "bar2")
    """
    try:
        return method_call(*method_vars)
    except Pyro.errors.ConnectionClosedError, x:
        logging.warning("Server is unreachable.")
        while 1:
            try:
                obj.adapter.bindToURI(obj.URI)
                logging.info("Server is back")
                return method_call(*method_vars)
            except Pyro.errors.ProtocolError:
                time.sleep(1)

