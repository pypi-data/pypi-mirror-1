# -*- coding: utf-8 -*-

import os, sys
from os import curdir

def fork2(pidfile):
    try:
        if os.fork() > 0:
            os._exit(0)
    except OSError, e:
        sys.exit('fork #1 failed: (%d) %s\n' % (e.errno, e.strerror))
    os.setsid()
    os.chdir(curdir)
    os.umask(002)
    try:
        if os.fork() > 0:
            os._exit(0)
    except OSError, e:
        sys.exit('fork #2 failed: (%d) %s\n' % (e.errno, e.strerror))
    si = open('/dev/null', 'r')
    so = open('/dev/null', 'w')
    sys.stdout.flush()
    sys.stderr.flush()
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(so.fileno(), sys.stderr.fileno())
    sys.stdout = sys.stderr = so
    fp = open(pidfile, 'w')
    fp.write(str(os.getpid()))
    fp.close()

