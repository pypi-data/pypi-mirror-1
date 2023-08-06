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


import Pyro.core
import time
import logging

from Queue import Queue
from threading import Thread
from subprocess import Popen, PIPE
from Pyro.errors import ConnectionClosedError

from aditam.agent.config import agent_config

class JobManager(Thread):
    """ Excute the jobs and send reports. """

    def __init__(self, host, port, hostname):
        """
        hostname : name of the agent
        """
        Thread.__init__(self)
        self.hostname = hostname
        self.server = Pyro.core.getProxyForURI("PYROLOC://%s:%s/server" % \
            (host, port))
        self.feedback = Pyro.core.getProxyForURI("PYROLOC://%s:%s/feedback"\
                % (host, port))

    def _is_command_ok(self, returncode):
        """
        Test if the command was execute succesfully.
        Return a boolean.
        """
        if not returncode:
            return True
        return False

    def unicode_encode(self, text, charsets):
        """
        Try to encode a string in unicode
        If the encoding failled this method return
        the original text
        """
        for charset in charsets:
            try:
                res = unicode(text, charset)
                return res
            except UnicodeDecodeError:
                pass
        logging.warning("unicode encode failled for '%s'" % text)
        return text
        
    def execute_job(self, agentjob):
        """
        Executes the commands and send a command report
        agentjob : an AgentJob object
        command_report : {'cmd_id', 'stdout', 'stderr', 'result'}
        """
        logging.info("Execute new job %d", agentjob.get_job_id())
        for command in agentjob.get_commands():
            command_report = dict(cmd_id=command['id'])
            p = Popen(command['command_line'],
                    shell=True,
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=PIPE)
            returncode = p.wait()
            stdout = self.unicode_encode(p.stdout.read(), ('utf-8', 'iso8859-15'))
            stderr = self.unicode_encode(p.stderr.read(), ('utf-8', 'iso8859-15'))
            p.stdin.close()
            p.stdout.close()
            p.stderr.close()
            command_report['stdout'] = stdout
            command_report['stderr'] = stderr
            command_report['result'] = returncode
            self.feedback.add_command_report(command_report,
                    agentjob.get_job_id())
            if not self._is_command_ok(returncode):
                logging.warning("Command '%s' failled !" % command['command_line'])
                self.feedback.end_job(agentjob.get_job_id(), False)
                return None
        self.feedback.end_job(agentjob.get_job_id())
        
    def run(self):
        """
        Loop which check new job.
        """
        logging.debug("Starting the jobmanager ...")
        while 1:
            try:
                agentjob = self.server.get_job(self.hostname)
            except ConnectionClosedError, e:
                logging.error(e)
                raise SystemExit(e)
            if agentjob:
                self.execute_job(agentjob)
            time.sleep(2)

