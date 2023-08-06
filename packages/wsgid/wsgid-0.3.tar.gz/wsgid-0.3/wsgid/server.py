

import os, subprocess, logging, signal, itertools, sys, time, pickle

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
    return app

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
        conf_dump = pickle.dumps(server_config)
        p = subprocess.Popen([sys.executable, __file__, '--reload-loop'],
            stdin=subprocess.PIPE)
        p.stdin.write(conf_dump)
        p.stdin.close()
        self.child_pid = p.pid
        return p

    def _reloader_loop(self, extra_files=None, interval=1):
        """When this function is run from the main thread, it will force other
        threads to exit when any modules currently loaded change.

        Copyright notice.  This function is based on the autoreload.py from
        the CherryPy trac which originated from WSGIKit which is now dead.

        :param extra_files: a list of additional files it should watch.
        """
        def iter_module_files():
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
                        yield filename, module

        mtimes = {}
        while self.running:
            for filename, module in itertools.chain(iter_module_files(), extra_files or ()):
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
        # muahahah
        if conf is None:
            conf = pickle.loads(sys.stdin.read())
        self.conf = conf
        self.server = create_server(conf)

    def _on_sig15(self, signum, frame):
        self.server.stop()

    def start(self):
        signal.signal(15, self._on_sig15)
        try:
            self.server.start()
        except KeyboardInterrupt:
            self.server.stop()
        os._exit(0)


def run_process_server():
    p = ServerProcess()
    p.start()

if __name__ == '__main__':
    if '--reload-loop' in sys.argv:
        run_process_server()

