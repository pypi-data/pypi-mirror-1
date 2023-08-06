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
__date__ = '$LastChangedDate: 2008-05-23 21:31:46 +0200 (Fri, 23 May 2008) $'
__version__ = '$Rev: 182 $'

"""
Manage all config files
"""

import os
import logging

from ConfigParser import ConfigParser
from aditam.core.config import Config

conf_name = "aditam-agent.conf"
conf_dirs = [".",
        os.path.join(os.path.expanduser("~"), ".aditam"),
        "C:\Program Files\Aditam",
        "/etc",
        "/etc/aditam"]

agent_config = Config(conf_name, conf_dirs, "aditam.agent")
