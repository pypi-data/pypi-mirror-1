
"""
wsgid.daemon
~~~~~~~~~~~~
"""

import sys, os, time, atexit, signal, errno, tempfile, subprocess
import logging
from logging import handlers

import simplejson


class DaemonAlreadyRunningError(RuntimeError):
    """The daemon is already running"""


class DaemonNotRunningError(RuntimeError):
    """The daemon is not running"""


def create_dummy_pidfile():
    fd, filename = tempfile.mkstemp(prefix='wsgid_', suffix='.pid')
    os.close(fd)
    return filename


def create_pidfile(pidfile):
    pid = os.getpid()
    f = open(pidfile, 'w')
    f.write('%s\n' % pid)
    f.close()


def remove_pidfile(pidfile):
    try:
        os.unlink(pidfile)
    except OSError:
        pass


def remove_pidfile_factory(pidfile):
    def _remove(pidfile=pidfile):
        remove_pidfile(pidfile)
    return _remove


def get_pid(pidfile):
    try:
        f = open(pidfile)
        pd = f.read()
        f.close()
        try:
            pid = int(pd)
        except ValueError:
            pid = None
    except IOError:
        pid = None
    return pid


def is_pid_running(pid):
    try:
        os.kill(pid, 0)
        running = True
    except OSError, err:
        running = (err.errno == errno.EPERM)
    return running


def is_daemon_running(pidfile):
    pid = get_pid(pidfile)
    if pid:
        if is_pid_running(pid):
            running = True
        else:
            remove_pidfile(pidfile)
            running = False
    else:
        running = False
    return running


def signal_daemon(pidfile, signum):
    if is_daemon_running(pidfile):
        pid = get_pid(pidfile)
        os.kill(pid, signum)
    else:
        raise DaemonNotRunningError(
            'No running daemon at pidfile %r.' % pidfile)


def stop_daemon(pidfile):
    signal_daemon(pidfile, 15)


log_format = ('%(asctime)s:%(levelname)8s:%(name)12s:%(process)d:'
              '%(message)s')


def create_logger(conf, name='daemon', filename='wsgid.log'):
    if not os.path.exists(conf.logdir):
        os.mkdir(conf.logdir)
    if conf.verbose:
        conf.loglevel = logging.DEBUG
    else:
        conf.loglevel = logging.INFO
    handler = handlers.RotatingFileHandler(
              os.path.join(conf.logdir, filename),
              maxBytes=200000, backupCount=20)
    formatter = logging.Formatter(log_format, '%d.%m.%Y:%H:%M:%S')
    handler.setFormatter(formatter)
    log = logging.getLogger(name)
    log.addHandler(handler)
    log.setLevel(conf.loglevel)

    if not conf.no_log_stdout:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        log.addHandler(handler)
    return log


def read_fd(fd, chunksize=1024):
    buffer = []
    running = True
    while running:
        chunk = os.read(fd, chunksize)
        buffer.append(chunk)
        running = len(chunk) == chunksize
    return ''.join(buffer)


class WSGIDaemon(object):

    def __init__(self, config):
        self.config = config
        self.stopped = False
        if not self.config.pidfile:
            self.config.pidfile = create_dummy_pidfile()
        self.pidfile = config.pidfile
        self.log = create_logger(config)
        self.log.debug('Initialized daemon.')
        for k, v in config.items():
            if v:
                self.log.debug('Config: %s=%r' % (k, v))
        self.log.debug('Listening on http://%s:%s.' % (config.host, config.port))

    def _on_signal_15(self, signum, frame):
        self.log.debug('Received signal 15. Will stop.')
        self.stop()
        self.log.info('Stopped.')

    def _on_exit(self):
        self.stop()

    def start(self):
        if is_daemon_running(self.pidfile):
            self.log.error('Daemon already running.')
            return 1
        else:
            self.log.debug('Starting daemon.')
            create_pidfile(self.config.pidfile)
            self.log.debug('Created PID File "%s".' % self.pidfile)
            signal.signal(15, self._on_signal_15)
            atexit.register(self._on_exit)
            self.log.debug('Registered signal handlers.')
            server_config = self.config
            self.child_pid = None
            self.child = None
            self.running = True
            if server_config.no_reloader:
                self.log.debug('Not using reloader.')
            else:
                self.log.debug('Using reloader.')
            self._wait_as_reloader()
            self.log.info('Daemon finished naturally.')
            return 0

    def stop(self):
        if not self.stopped:
            self.running = False
            self._stop_child()
            remove_pidfile(self.pidfile)
            self.log.debug('Exited. Removing PID file "%s".' % self.pidfile)
            self.stopped = True

    def _stop_child(self):
        self.log.debug('Stopping server.')
        if self.child_pid is not None:
            os.kill(self.child_pid, 15)
            time.sleep(1)
            try:
                os.kill(self.child_pid, 9)
            except OSError:
                pass
        if self.child is not None:
            try:
                self.child.communicate()
            except KeyboardInterrupt:
                self.log.warn('Ok, if you say so. Killing')
                os.kill(self.child.pid, 9)
            returncode = self.child.returncode
            self._child_waited()
            return returncode

    def _child_waited(self):
        self.log.debug('Server exited with code %s. '
                        % self.child.returncode)
        self.child = None
        self.child_pid = None

    def _wait_as_reloader(self):
        while self.running:
            if not self.child:
                p = self._fork_server(self.config)
            if not p:
                self.running = False
                continue
            try:
                changed_filename = self._reloader_loop()
            except KeyboardInterrupt:
                print # to make it pretty on stdout
                self.log.info('Received Keyboard Interrupt.')
                self.running = False
                continue
            if not self.config.no_reloader and self.running:
                self.log.info('Reloading for change to %r.' % changed_filename)
                self._stop_child()

    def _fork_server(self, server_config):
        self.log.debug('Spawning server.')
        inpath, outpath = create_pipe_names()

        runner = os.path.join(os.path.dirname(__file__), 'server.py')

        p = subprocess.Popen([sys.executable, runner, '--reload-loop', outpath, inpath],
            stdout=sys.stdout,
            stderr=sys.stderr,
            stdin=subprocess.PIPE,
            env=os.environ.copy())

        create_pipes(inpath, outpath)
        fin, fout = open_pipes(inpath, outpath)

        conf_dump = simplejson.dumps(server_config.to_dict())
        os.write(fout, conf_dump)

        d = read_fd(fin)
        try:
            modules_list = simplejson.loads(d)
        except Exception, e:
            self.log.error('Could not start server.')
            retcode = p.wait()
            self._child_waited(retcode)
            return
        self.modules_list = modules_list
        self.child_pid = p.pid
        self.child = p

        os.close(fin)
        os.close(fout)
        os.unlink(inpath)
        os.unlink(outpath)
        return p

    def _reloader_loop(self, extra_files=None, interval=1):
        mtimes = {}
        while self.running:
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



def create_temp_path():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    os.unlink(path)
    return path

def create_pipe_names():
    return create_temp_path(), create_temp_path()

def create_pipes(inpath, outpath):
    os.mkfifo(inpath)
    os.mkfifo(outpath)

def open_pipes(inpath, outpath):
    flags = os.O_RDWR | os.O_SYNC
    f1 = os.open(inpath, flags)
    f2 = os.open(outpath, flags)
    return f1, f2



