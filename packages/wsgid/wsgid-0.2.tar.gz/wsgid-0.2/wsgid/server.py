

import os, subprocess, logging

from daemon import Daemon, stop_daemon, DaemonConfig
from cherryserver import CherryPyWSGIServer as WSGIServer
from utils import import_string


if (hasattr(os, "devnull")):
   REDIRECT_TO = os.devnull
else:
   REDIRECT_TO = "/dev/null"


class ServerConfig(object):

    server_name = ''
    host = '0.0.0.0'
    port = 9090

    app_factory_import_string = None
    app_import_string = None

    loglevel = logging.DEBUG
    logdir = os.getcwd()

    std_redirect_file = REDIRECT_TO

    workdir = os.getcwd()

    umask = 0

def default_app_factory():
    def app(environ, start_response):
        start_response('200 OK', [('content-type', 'text/plain')])
        return ['hello', 'world']
    return app

def get_app(conf):
    if conf.application:
        app = import_string(self.application)
    else:
        if conf.application_factory:
            app_factory = import_string(conf.application_factory)
        else:
            app_factory = default_app_factory
        app = app_factory()
    return app

def create_server(conf):
    return WSGIServer(
        (conf.host, conf.port),
        get_app(conf),
        server_name = conf.servername
    )

def create_daemon_config(self):
    return self


class WSGIDaemon(Daemon):

    def do_start(self, server_config):
        self.server = create_server(server_config)
        try:
            self.server.start()
        except KeyboardInterrupt:
            stop_daemon(self.pidfile)

    def do_stop(self):
        self.server.stop()


