# -*- coding: utf-8 -*-

from __future__ import with_statement
from threading import Thread, Lock
from _superfcgi import Request
import socket, sys, logging, traceback, signal, time, os


logger = logging.getLogger('FASTCGI')


class Handler(Thread):

    _environ = {
        'wsgi.version': (1, 0),
        'wsgi.multithread': True,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
        }

    def __init__(self, worker):
        super(Handler, self).__init__()
        self.worker = worker
        self.sock_fd = worker.sock_fd
        self.app = worker.app

    def run(self):
        request = Request(self.sock_fd)
        while True:
            try:
                request.accept()
            except IOError, e:
                # one of the reason - dead socket
                return
            try:
                self.handle(request)
            except Exception, e:
                logger.exception(e)
                try:
                    request.stdout.write('Status: 500\r\n')
                    request.stdout.write('\r\n')
                    request.stdout.write('<html><head></head><body><h1>500</h1></body></html>')
                    request.stdout.write('\r\n')
                    request.stdout.flush()
                except IOError,e:
                    logger.exception(e)

    def handle(self, req):
        environ = req.environ
        environ['wsgi.input'] = req.stdin
        environ['wsgi.errors'] = req.stderr
        environ.update(self._environ)

        if environ.get('HTTPS', 'off') in ('on', '1'):
            environ['wsgi.url_scheme'] = 'https'
        else:
            environ['wsgi.url_scheme'] = 'http'

        headers_set = []
        headers_sent = []

        def write(data):

            if not headers_set:
                raise AssertionError('write() before start_response()')

            elif not headers_sent:
                # Before the first output, send the stored headers
                status, response_headers = headers_sent[:] = headers_set
                req.stdout.write('Status: %s\r\n' % status)
                for header in response_headers:
                    req.stdout.write('%s: %s\r\n' % header)
                req.stdout.write('\r\n')

            req.stdout.write(data)
            try:
                req.stdout.flush()
            except IOError:
                # user closed his tab and connection is closed before we flush
                pass

        def start_response(status, response_headers, exc_info=None):
            if exc_info:
                try:
                    if headers_sent:
                        # Re-raise original exception if headers sent
                        raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    exc_info = None # avoid dangling circular ref
            elif headers_set:
                raise AssertionError('Headers already set!')

            headers_set[:] = [status,response_headers]
            return write

        result = self.app(environ, start_response)
        try:
            for data in result:
                if data: # don't send headers until body appears
                    write(data)
            if not headers_sent:
                write('') # send headers now if body was empty
        finally:
            if hasattr(result, 'close'):
                result.close() 


class Worker(object):

    handler_class = Handler

    def __init__(self, master):
        self.master = master
        self.handlers = []
        self.sock_fd = master.sock_fd
        self.pid = None
        self.timeout = 0.1

    def start(self):
        try:
            pid = os.fork()
        except OSError, e:
            raise RuntimeError("Worker fork failed")
        if pid > 0:
            self.pid = pid
            return pid
        self.run()

    def import_app(self):
        chunks = self.master.app.split('.')
        self.app = getattr(__import__('.'.join(chunks[:-1]), [], [], ['*']),
                           chunks[-1])

    def run(self):
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        self.import_app()
        for index in range(self.master.threads):
            handler = self.handler_class(self)
            handler.start()
            self.handlers.append(handler)
        while True:
            for i, handler in enumerate(self.handlers):
                handler.join(self.timeout)
                if not handler.is_alive():
                    logger.info('Worker %s: handler %s is dead, trying to restart' % (self.pid, handler))
                    newhandler = self.handler_class(self)
                    newhandler.start()
                    self.handlers[i] = newhandler

    def stop(self, *args, **kwargs):
        os._exit(os.EX_OK)

class WorkerMonitor(Thread):

    def __init__(self, master):
        super(WorkerMonitor, self).__init__()
        self.master = master
        self.worker_class = master.worker_class
        self.terminate = False
        self.worker_pid = None

    def run(self):
        while not self.terminate:
            logger.info('Monitor %s: starting/restarting worker' % self)
            self.worker = self.worker_class(self.master)
            try:
                self.worker_pid = self.worker.start()
                if self.worker_pid is None:
                    logger.info('Monitor %s: worker pid is None' % self)
                    return
                logger.info('Monitor %s: worker %s started' % (self, self.worker_pid))
            except RuntimeError:
                logger.info('Monitor %s: Worker failed to start' % self)
                return
            while not self.terminate:
                try:
                    oldpid, status = os.waitpid(self.worker_pid, os.WNOHANG)
                    time.sleep(1)
                except OSError,e:
                    # process is dead
                    if not self.terminate:
                        break


class FastCGIMaster(object):

    worker_class = Worker
    workers = 2
    threads = 3
    sock_fd = 0

    def __init__(self, app, sock=None, **kwargs):
        self.app = app
        if sock is not None:
            self.sock_fd = sock.fileno()
        self.sock_family = sock.family
        self.sock_type = sock.type
        self.monitors = []
        self.terminate = False
        self.__dict__.update(kwargs)

    def import_app(self):
        chunks = self.app.split('.')
        getattr(__import__('.'.join(chunks[:-1]), [], [], ['*']),
                           chunks[-1])

    def start(self):
        try:
            self.import_app()
        except SyntaxError:
            logger.error('Exception while import "%s"' % self.app)
            return
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        for index in range(self.workers):
            monitor = WorkerMonitor(self)
            monitor.start()
            self.monitors.append(monitor)
        while not self.terminate:
            time.sleep(1)

    def stop(self, *args, **kwargs):
        logger.info('Terminating superfcgi')
        for monitor in self.monitors:
            logger.info('Terminating monitor %s' % monitor)
            monitor.terminate = True
            if monitor.is_alive():
                if monitor.worker_pid is not None:
                    logger.info('killing worker %s' %  monitor.worker_pid)
                    os.kill(monitor.worker_pid, signal.SIGTERM)
        self.terminate = True
