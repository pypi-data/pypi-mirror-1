

import os, sys, signal

import simplejson

from daemon import read_fd, open_pipes, create_logger
from utils import import_string
from config import Config
from main import options


def default_app_factory():
    def app(environ, start_response):
        start_response('200 OK', [('content-type', 'text/plain')])
        return ['hello', '\n', 'world']
    return app

default_app = default_app_factory()


class LoggedApp(object):

    def __init__(self, conf, app):
        self.conf = conf
        self.app = app
        self.log = create_logger(conf, 'access')

    def __call__(self, environ, start_response):
        self.log.info('%s %s' % (environ['SCRIPT_NAME'], environ['PATH_INFO']))
        return self.app(environ, start_response)

def logged_app(conf, oldapp):
    log = create_logger(conf, '')
    def app(environ, start_response, oldapp=oldapp, log=log):
        #log.info('%s %s' % (environ['SCRIPT_NAME'], environ['PATH_INFO']))
        return oldapp(environ, start_response)
    return app


def get_app(conf):
    if conf.application:
        app = import_string(conf.application)
    else:
        if conf.application_factory:
            app_factory = import_string(conf.application_factory)
            app = app_factory()
        else:
            app = default_app_factory()

    if conf.debug:
        app = debugged_app(app)

    #app = LoggedApp(conf, app)

    return app


def create_config(conf_data):
    conf = Config(options)
    conf.from_dict(conf_data)
    return conf

def debugged_app(app):
    from werkzeug.debug import DebuggedApplication
    return DebuggedApplication(app, True)

class BaseWSGIServer(object):

    name = 'unnamed'

    def __init__(self, conf, app):
        self.conf = conf
        self.app = app
        self.log = create_logger(conf, self.name)
        self.log.info('Starting %r server' % self.name)

    def start(self):
        pass

    def stop(self):
        pass



def activate_virtualenv(env):
    activate_script = os.path.join(env, 'bin', 'activate_this.py')
    execfile(activate_script, dict(__file__=activate_script))


class ServerProcess(object):
    def __init__(self, inpath, outpath):
        fin, fout = open_pipes(inpath, outpath)
        data = read_fd(fin)
        conf_data = simplejson.loads(data)
        conf = self.conf = create_config(conf_data)
        self.log = create_logger(conf, name='server')
        self.log.debug('Server process started.')

        if not (conf.application or conf.application_factory):
            self.log.warning('No application, or application_factory -> Hello World.')
        if conf.virtualenv:
            self.log.debug('Using virtualenv: %r' % conf.virtualenv)
            activate_virtualenv(conf.virtualenv)

        app = get_app(conf)
        self.server = self._create_server(app)

        if conf.ssl_certificate or conf.ssl_private_key:
            if conf.ssl_certificate and conf.ssl_private_key:
                self.server.ssl_certificate = conf.ssl_certificate
                self.server.ssl_private_key = conf.ssl_private_key
            else:
                log.warn('Must provide both ssl_certificate and ssl_private_key '
                         'for SSL support. Disabled.')

        module_filenames = simplejson.dumps(list(self._iter_module_filenames()))
        os.write(fout, module_filenames)
        os.close(fin)
        os.close(fout)

    def _on_sig15(self, signum, frame):
        self.log.debug('Server received SIG 15.')
        self.server.stop()

    def _pretty_display(self):
        opts = self.conf.to_dict()
        opts.update(dict(
            app = self.conf.application or self.conf.application_factory or 'Hello World',
            reloader = not self.conf.no_reloader,
            ve = self.conf.virtualenv or 'None',
            ssl = len(self.conf.ssl_certificate and self.conf.ssl_private_key) > 0,
            h = ((self.conf.host == u'0.0.0.0') and '*') or self.conf.host
        ))
        self.log.info(
            'Listening: %(h)s:%(port)s, '
            'app=%(app)r ssl=%(ssl)d, rld=%(reloader)d, dbg=%(debug)d, '
            'venv=%(ve)s' % opts)

    def start(self):
        self._pretty_display()
        signal.signal(15, self._on_sig15)
        try:
            self.server.start()
        except KeyboardInterrupt:
            self.log.debug('Server received KeyboardInterrupt.')
            self.server.stop()
        self.log.debug('Server ended.')
        self.server.stop()

    def _iter_module_filenames(self):
        """Get a list of all files in use"""
        for module in sys.modules.values():
            filename = getattr(module, '__file__', None)
            if filename:
                while not os.path.isfile(filename):
                    filename = os.path.dirname(filename)
                    if not filename:
                        break
                else:
                    if filename[-4:] in ('.pyc', '.pyo'):
                        filename = filename[:-1]
                    yield filename

    def _create_server(self, app):
        try:
            WSGIServer = import_string('wsgid.servers.%s:WSGIServer'
                                       % self.conf.server)
        except ImportError, e:
            self.log.warning('Chosen server %r not available: %s' %
                             (self.conf.server, e))
            WSGIServer = import_string('wsgid.servers.cherrypy:WSGIServer')
        server = WSGIServer(self.conf, app)
        return server



def run_process_server(inpath, outpath):
    p = ServerProcess(inpath, outpath)
    p.start()


if __name__ == '__main__':
    if '--reload-loop' in sys.argv:
        run_process_server(*sys.argv[sys.argv.index('--reload-loop') + 1:])

