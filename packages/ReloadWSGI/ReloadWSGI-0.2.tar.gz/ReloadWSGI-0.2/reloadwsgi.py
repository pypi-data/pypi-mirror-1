#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Robust WSGI auto-reloading for development.
#
# Reload a WSGI application on source change. Keep the old code alive
# when the change has syntax errors. Never close the socket, never refuse
# a connection.
#
# Replacement for 'paster serve --reload config.ini'
#
# Daniel Holth <dholth@fastmail.fm>

import os
import sys
import logging.config
import time
import threading
import ConfigParser
from Queue import Empty

from multiprocessing import Process, Queue, Event
from multiprocessing import active_children
from optparse import OptionParser
from wsgiref.simple_server import make_server

import paste.deploy
import paste.reloader

class Monitor(paste.reloader.Monitor):
    def __init__(self, poll_interval=1, tx=None, rx=None):
        paste.reloader.Monitor.__init__(self, poll_interval)
        self.state = 'RUN'
        self.tx = tx
        self.rx = rx

    def periodic_reload(self):
        while not self.rx.is_set():
            if not self.check_reload():
                self.state = 'STANDBY'
                # inform code change
                self.tx.put({'pid':os.getpid(), 'status':'changed'})
                self.rx.wait(10)
                if self.rx.is_set():
                    return
                self.state = 'RUN'
                self.module_mtimes = {}
            time.sleep(self.poll_interval) 

def serve(server, uri, tx, rx):
    try:
        # configure logging
        config_file = uri
        if config_file.startswith('config:'):
            config_file = config_file.split(':', 1)[1]
        parser = ConfigParser.ConfigParser()
        parser.read([config_file])
        if parser.has_section('loggers'):
            logging.config.fileConfig(config_file)

        # load wsgi application
        app = paste.deploy.loadapp(uri)

        tx.put({'pid':os.getpid(), 'status':'loaded'})

        server.set_app(app)

        t = threading.Thread(target=server.serve_forever)
        t.setDaemon(True)
        t.start()

        monitor = Monitor(tx=tx, rx=rx)
        monitor.periodic_reload()

    except KeyboardInterrupt:
        pass

def reloadwsgi(uri, host='localhost', port=8080):
    server = make_server(host, port, None)
    
    # tx, rx from the subprocess' perspective.
    tx = Queue()

    def spinup():
        rx = Event()
        worker = Process(target=serve, args=(server, uri, tx, rx))
        worker.rx = rx
        worker.start()
        return worker

    spinup()

    while True:
        try:
            msg = tx.get(True, 1)
            sys.stderr.write("%r\n" % msg)
            if msg['status'] == 'changed':
                spinup()
            elif msg['status'] == 'loaded':
                for worker in active_children():
                    if worker.ident != msg['pid']:
                        worker.rx.set()
        except Empty:
            if not active_children():
                return

def main():
    import optparse
    import os.path
    usage = """Usage: %prog [options] config.ini
Robust automatic reloading for WSGI development."""
    parser = optparse.OptionParser(usage)
    parser.add_option("-H", "--host", dest="hostname",
            default="localhost", type="string",
            help="Listen on hostname/address instead of localhost")
    parser.add_option("-p", "--port", dest="port",
            default=8080, type="int",
            help="Listen on port instead of 8080")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Must specify exactly one Paste Deploy .ini file.")
    host = options.hostname
    port = options.port
    config = os.path.abspath(args[0])
    reloadwsgi('config:%s' % config, host=host, port=port)

def app_factory(global_config, **local_conf):
    import wsgiref.simple_server
    return wsgiref.simple_server.demo_app

if __name__ == "__main__":
    import reloadwsgi
    import pkg_resources
    import os.path
    resource = pkg_resources.resource_filename(__name__, 'test_reloadwsgi.ini')
    resource = os.path.abspath(resource)
    reloadwsgi.reloadwsgi('config:%s' % resource)
