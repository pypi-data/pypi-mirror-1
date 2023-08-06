# -*- coding: utf-8 -*-

from optparse import OptionParser
from server import FastCGIMaster
from fork2 import fork2
import re, sys, socket, os
import logging
import logging.handlers


parser = OptionParser()

parser.add_option('-a', '--app', action='store', type='string',
                  dest='app', help='import string for wsgi app')
parser.add_option('-s', '--socket', action='store', type='string',
                  dest='socket', help='unix socket or ip:port')
parser.add_option('-w', '--workers', action='store', type='int',
                  dest='workers', default=4, help='number of superfcgi workers,'\
                      ' default is %default')
parser.add_option('-t', '--threads', action='store', type='int',
                  dest='threads', default=10, help='number of threads inside each worker,'\
                      ' default is %default')
parser.add_option('-b', '--backlog', action='store', type='int',
                  dest='backlog', default=socket.SOMAXCONN, help='backlog size, default is %default')
parser.add_option('-p', '--path', action='append', type='string',
                  dest='path', help='optional path should be added in sys.path')
parser.add_option('-l', '--log', action='store', type='string',
                  dest='log', help='log file')
parser.add_option('-d', '--daemonize', action='store', type='string', dest='daemon')
parser.add_option('--pidfile', action='store', type='string', dest='pidfile')


def run():
    opts, args = parser.parse_args()
    assert opts.app and opts.socket
    if opts.log:
        log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_handler = logging.handlers.FileHandler(opts.log)
        log_handler.setFormatter(log_formatter)
        log_handler.setLevel(logging.INFO)
        logger = logging.getLogger('FASTCGI')
        logger.addHandler(log_handler)
        logger.setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)
    for path in opts.path:
        sys.path.insert(0, path)
    if re.match(r'\d+\.\d+\.\d+\.\d+:\d+', opts.socket):
        _socket = opts.socket.split(':')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((_socket[0], int(_socket[1])))
    else:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(opts.socket)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.listen(opts.backlog)
    if opts.daemon and opts.daemon.lower() in ('yes', 'true', 'on', 'jquery'):
        if not opts.pidfile:
            raise Exception('If you want to daemonize, please provide "pidfile" name')
        fork2(opts.pidfile)
    server = FastCGIMaster(app=opts.app, sock=sock,
                           workers=opts.workers, threads=opts.threads)
    server.start()


if __name__ == '__main__':
    run()
