#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Timo Stollenwerk (timo@zmag.de)"
__license__ = "GNU General Public License (GPL)"
__revision__ = "$Rev$"
__date__ = "$Date$"
__URL__ = "$URL$"

import sys
import tempfile

from subprocess import Popen, PIPE
from logger import LOG

win32 = (sys.platform=='win32')


def newTempfile(suffix=''):
    return tempfile.mktemp(suffix=suffix)


def runcmd(cmd):
    """ Execute a command using the subprocess module """

    if win32:

        cmd = cmd.replace('\\', '/')
        s = Popen(cmd, shell=False)
        s.wait()
        return 0, ''

    else:

        stdin = open('/dev/null')
        stdout = stderr = PIPE

        p = Popen(cmd,
                  shell=True,
                  stdin=stdin,
                  stdout=stdout,
                  stderr=stderr,
                  )

        status = p.wait()
        stdout_ = p.stdout.read().strip()
        stderr_ = p.stderr.read().strip()

        if stdout_:
            LOG.info(stdout_)
        if stderr_:
            LOG.info(stderr_)
        return status, stdout_ + stderr_

