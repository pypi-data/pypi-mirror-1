

import os, subprocess, logging, signal, itertools, sys, time

import simplejson

from daemon import Daemon, stop_daemon, DaemonConfig
from cherryserver import CherryPyWSGIServer as WSGIServer
from utils import import_string
from config import Config


if (hasattr(os, "devnull")):
   REDIRECT_TO = os.devnull
else:
   REDIRECT_TO = "/dev/null"



def default_app_factory():
    def app(environ, start_response):
        start_response('200 OK', [('content-type', 'text/plain')])
        return ['hello', '\n', 'world']
    return app

def get_app(conf):
    if conf.application:
        app = import_string(conf.application)
    else:
        if conf.application_factory:
            app_factory = import_string(conf.application_factory)
        else:
            app_factory = default_app_factory
        app = app_factory()

    if conf.debug:
        app = debugged_app(app)
    return app


def debugged_app(app):
    from werkzeug.debug import DebuggedApplication
    return DebuggedApplication(app, True)

def create_server(conf):
    return WSGIServer(
        (conf.host, conf.port),
        get_app(conf),
        server_name = conf.servername
    )


def start_server(conf):
    server = create_server(conf)

    server.start()



class WSGIDaemon(Daemon):

    def do_stop(self):
        self._stop_child()
        self.running = False

    def do_start(self, server_config):
        self.running = True
        if server_config.reloader:
            self._wait_as_reloader()
        else:
            self._wait_on_child()

    def _stop_child(self):
        os.kill(self.child_pid, 15)

    def _wait_on_child(self):
        p = self._fork_server(self.config)
        try:
            p.wait()
        except KeyboardInterrupt:
            self._stop_child()
            p.wait()

    def _wait_as_reloader(self):
        while self.running:
            p = self._fork_server(self.config)
            try:
                changed_filename = self._reloader_loop()
            except KeyboardInterrupt:
                self._stop_child()
                return
            self.log.info('Reloading for change to %r.' % changed_filename)
            self._stop_child()
            p.wait()

    def _fork_server(self, server_config):
        p = subprocess.Popen([sys.executable, __file__, '--reload-loop'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=open(os.path.join(server_config.logdir, 'server_errors.log'), 'a'))
        conf_dump = simplejson.dumps(server_config.to_dict())
        p.stdin.write(conf_dump)
        p.stdin.close()
        d = p.stdout.read()
        modules_list = simplejson.loads(d)
        self.modules_list = modules_list
        self.child_pid = p.pid
        self.child = p
        return p

    def _reloader_loop(self, extra_files=None, interval=1):
        mtimes = {}
        while self.running:
            #for filename in itertools.chain(iter_module_files(), extra_files or ()):
            for filename in self.modules_list:
                try:
                    mtime = os.stat(filename).st_mtime
                except OSError:
                    continue

                old_time = mtimes.get(filename)
                if old_time is None:
                    mtimes[filename] = mtime
                    continue
                elif mtime > old_time:
                    return filename
            time.sleep(interval)




class ServerProcess(object):

    def __init__(self, conf=None):

        if conf is None:
            data = sys.stdin.read()
            conf_data = simplejson.loads(data)
            from main import options
            conf = Config(options)
            conf.from_dict(conf_data)
            sys.stderr.write('%s\n\n' % list(conf.items()))
            sys.stderr.write('%s\n\n' % conf_data)
        self.conf = conf
        self.server = create_server(conf)

        if conf.ssl_certificate and conf.ssl_private_key:
            self.server.ssl_certificate = conf.ssl_certificate
            self.server.ssl_private_key = conf.ssl_private_key

        module_filenames = simplejson.dumps(list(self._iter_module_filenames()))
        sys.stdout.write(module_filenames)
        sys.stdout.flush()
        os.close(sys.stdout.fileno())


    def _on_sig15(self, signum, frame):
        self.server.stop()

    def start(self):
        signal.signal(15, self._on_sig15)
        try:
            self.server.start()
        except KeyboardInterrupt:
            self.server.stop()
        os._exit(0)

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


def run_process_server():
    p = ServerProcess()
    p.start()

if __name__ == '__main__':
    if '--reload-loop' in sys.argv:
        run_process_server()

