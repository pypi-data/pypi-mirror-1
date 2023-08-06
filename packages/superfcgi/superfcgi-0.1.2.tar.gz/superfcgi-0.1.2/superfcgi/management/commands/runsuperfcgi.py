# -*- coding: utf-8 -*-

import sys
import socket
import os
from django.core.management.base import BaseCommand
import django.core.handlers.wsgi

# This is our wsgi app
app = django.core.handlers.wsgi.WSGIHandler()

FASTCGI_HELP = r"""
  Run this project as a fastcgi.

   superfcgi [options] [fcgi settings]

Optional Fcgi settings: (setting=value)
  workers=INT          number of worker proceses.
  threads=INT          number of threads on each worker.
  host=HOSTNAME        hostname to listen on..
  port=PORTNUM         port to listen on.
  socket=FILE          UNIX socket to listen on.
  daemonize=BOOL       whether to detach from terminal.
  pidfile=FILE         write the spawned process-id to this file.
  workdir=DIRECTORY    change to this directory when daemonizing.
  outlog=FILE          write stdout to this file.
  errlog=FILE          write stderr to this file.
  umask=UMASK          umask to use when daemonizing (default 022).

Examples:
  Run a fastcgi server on a UNIX domain socket (posix platforms only)
    $ manage.py runsuperfcgi socket=/tmp/fcgi.sock

  Run a fastCGI as a daemon and write the spawned PID in a file
    $ manage.py runsuperfcgi socket=/tmp/fcgi.sock daemonize=true \
            pidfile=/var/run/django-fcgi.pid

"""
FASTCGI_OPTIONS = {
    'app': 'wsgi.app',
    'workers': 4,
    'threads': 10,
    'host': None,
    'port': None,
    'socket': None,
    'daemonize': None,
    'workdir': '/',
    'pidfile': None,
    'outlog': None,
    'errlog': None,
    'umask': None,
}



class Command(BaseCommand):
    help = "Runs this project as a FastCGI application."
    args = '[various KEY=val options, use `runsuperfcgi help` for help]'

    def handle(self, *args, **options):
        from django.conf import settings
        fcgi_options = FASTCGI_OPTIONS.copy()
        for x in args:
            if "=" in x:
                k, v = x.split('=', 1)
            else:
                k, v = x, True
            fcgi_options[k.lower()] = v

        if "help" in fcgi_options:
            print self.usage(None)
            return False

        sock = None
        if fcgi_options['host']:
            if fcgi_options['port']:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(fcgi_options['host'], int(fcgi_options['port']))
            else:
                print "Please specify port number for host '%s'" %\
                      fcgi_options.get('host','')
                return False

        if fcgi_options['socket']:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind(fcgi_options['socket'])

        if sock:
            sock.listen(socket.SOMAXCONN)
        else:
            print "Please specify unix socket (host and port) to run fastcgi on"
            return False

        try:
            from superfcgi.server import FastCGIMaster
        except ImportError:
            print >> sys.stderr, "Unable to load superfcgi package"
            return False

        app = 'superfcgi.management.commands.runsuperfcgi.app'
        threads = int(fcgi_options['threads'])
        workers = int(fcgi_options['workers'])

        daemon_kwargs = {}
        if fcgi_options['outlog']:
            daemon_kwargs['out_log'] = fcgi_options['outlog']
        if fcgi_options['errlog']:
            daemon_kwargs['err_log'] = fcgi_options['errlog']
        if fcgi_options['umask']:
            daemon_kwargs['umask'] = int(fcgi_options['umask'])

        if fcgi_options['daemonize']:
            from django.utils.daemonize import become_daemon
            become_daemon(our_home_dir=fcgi_options["workdir"], **daemon_kwargs)

        if fcgi_options["pidfile"]:
            fp = open(fcgi_options["pidfile"], "w")
            fp.write("%d\n" % os.getpid())
            fp.close()

        server = FastCGIMaster(app=app, sock=sock, threads=threads, workers=workers)
        server.start()

    def usage(self, subcommand):
        return FASTCGI_HELP
