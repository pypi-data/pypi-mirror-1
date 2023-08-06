
"""
wsgid.daemon
~~~~~~~~~~~~
"""

import sys, os, time, atexit, signal, errno
import logging, logging.handlers


class DaemonAlreadyRunningError(RuntimeError):
    """The daemon is already running"""


class DaemonNotRunningError(RuntimeError):
    """The daemon is not running"""


def create_pidfile(pidfile):
    pid = os.getpid()
    f = open(pidfile, 'w')
    f.write('%s\n' % pid)
    f.close()


def remove_pidfile(pidfile):
    os.unlink(pidfile)


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


UMASK = 0
MAXFD = 1024


def daemonize(redirect, workdir, umask):
    """Detach a process from the controlling terminal and run it in the
    background as a daemon.
    """

    try:
       # Fork a child process so the parent can exit.  This returns control to
       # the command-line or shell.  It also guarantees that the child will not
       # be a process group leader, since the child receives a new process ID
       # and inherits the parent's process group ID.  This step is required
       # to insure that the next call to os.setsid is successful.
       pid = os.fork()
    except OSError, e:
       raise Exception, "%s [%d]" % (e.strerror, e.errno)

    if (pid == 0):	# The first child.
       # To become the session leader of this new session and the process group
       # leader of the new process group, we call os.setsid().  The process is
       # also guaranteed not to have a controlling terminal.
       os.setsid()
 
       # Is ignoring SIGHUP necessary?
       #
       # It's often suggested that the SIGHUP signal should be ignored before
       # the second fork to avoid premature termination of the process.  The
       # reason is that when the first child terminates, all processes, e.g.
       # the second child, in the orphaned group will be sent a SIGHUP.
       #
       # "However, as part of the session management system, there are exactly
       # two cases where SIGHUP is sent on the death of a process:
       #
       #   1) When the process that dies is the session leader of a session that
       #      is attached to a terminal device, SIGHUP is sent to all processes
       #      in the foreground process group of that terminal device.
       #   2) When the death of a process causes a process group to become
       #      orphaned, and one or more processes in the orphaned group are
       #      stopped, then SIGHUP and SIGCONT are sent to all members of the
       #      orphaned group." [2]
       #
       # The first case can be ignored since the child is guaranteed not to have
       # a controlling terminal.  The second case isn't so easy to dismiss.
       # The process group is orphaned when the first child terminates and
       # POSIX.1 requires that every STOPPED process in an orphaned process
       # group be sent a SIGHUP signal followed by a SIGCONT signal.  Since the
       # second child is not STOPPED though, we can safely forego ignoring the
       # SIGHUP signal.  In any case, there are no ill-effects if it is ignored.
       #
       # import signal           # Set handlers for asynchronous events.
       # signal.signal(signal.SIGHUP, signal.SIG_IGN)
 
       try:
          # Fork a second child and exit immediately to prevent zombies.  This
          # causes the second child process to be orphaned, making the init
          # process responsible for its cleanup.  And, since the first child is
          # a session leader without a controlling terminal, it's possible for
          # it to acquire one by opening a terminal in the future (System V-
          # based systems).  This second fork guarantees that the child is no
          # longer a session leader, preventing the daemon from ever acquiring
          # a controlling terminal.
          pid = os.fork()	# Fork a second child.
       except OSError, e:
          raise Exception, "%s [%d]" % (e.strerror, e.errno)
 
       if (pid == 0):	# The second child.
          # Since the current working directory may be a mounted filesystem, we
          # avoid the issue of not being able to unmount the filesystem at
          # shutdown time by changing it to the root directory.
          os.chdir(workdir)
          # We probably don't want the file mode creation mask inherited from
          # the parent, so we give the child complete control over permissions.
          os.umask(umask)
       else:
          # exit() or _exit()?  See below.
          os._exit(0)	# Exit parent (the first child) of the second child.
    else:
       # exit() or _exit()?
       # _exit is like exit(), but it doesn't call any functions registered
       # with atexit (and on_exit) or any registered signal handlers.  It also
       # closes any open file descriptors.  Using exit() may cause all stdio
       # streams to be flushed twice and any temporary files may be unexpectedly
       # removed.  It's therefore recommended that child branches of a fork()
       # and the parent branch(es) of a daemon use _exit().
       os._exit(0)	# Exit parent of the first child.
 
    # Close all open file descriptors.  This prevents the child from keeping
    # open any file descriptors inherited from the parent.  There is a variety
    # of methods to accomplish this task.  Three are listed below.
    #
    # Try the system configuration variable, SC_OPEN_MAX, to obtain the maximum
    # number of open file descriptors to close.  If it doesn't exists, use
    # the default value (configurable).
    #
    # try:
    #    maxfd = os.sysconf("SC_OPEN_MAX")
    # except (AttributeError, ValueError):
    #    maxfd = MAXFD
    #
    # OR
    #
    # if (os.sysconf_names.has_key("SC_OPEN_MAX")):
    #    maxfd = os.sysconf("SC_OPEN_MAX")
    # else:
    #    maxfd = MAXFD
    #
    # OR
    #
    # Use the getrlimit method to retrieve the maximum file descriptor number
    # that can be opened by this process.  If there is not limit on the
    # resource, use the default value.
    #
    #
    sys.stdout.flush()
    sys.stderr.flush()

    import resource		# Resource usage information.
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
       maxfd = MAXFD

    # Iterate through and close all file descriptors.
    for fd in range(0, maxfd):
       try:
          os.close(fd)
       except OSError:	# ERROR, fd wasn't open to begin with (ignored)
          pass

    # Redirect all standard IO to a single file
    # Apparently this is good
    std_fd = os.open(redirect, os.O_RDWR)
    os.dup2(std_fd, 0)
    os.dup2(std_fd, 1)
    os.dup2(std_fd, 2)

    return(0)

log_format = ('%(levelname)s:%(asctime)s:PID=%(process)d\n'
              '%(message)s\n%(pathname)s:%(lineno)s:'
              '%(module)s.%(funcName)s\n--')

def create_logger(logdir, level=logging.INFO, name='daemon'):
    handler = logging.handlers.RotatingFileHandler(
              os.path.join(logdir, '%s.log' % name),
              maxBytes=200000, backupCount=20)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    log = logging.getLogger(name)
    log.addHandler(handler)
    log.setLevel(level)
    return log

class DaemonConfig(object):

    pidfile = None
    logdir = None
    std_redirect_file = None
    workdir = None
    umask = None

class Daemon(object):

    def __init__(self, config):
        self.config = config
        self.pidfile = config.pidfile
        self.log = create_logger(config.logdir, config.loglevel)
        self.log.info('Initialized daemon.')

    def _on_signal_15(self, signum, frame):
        self.log.debug('Received signal 15. Will stop.')
        self.do_stop()
        self.log.info('Stopped.')

    def _on_exit(self):
        remove_pidfile(self.pidfile)
        self.log.debug('Exited. Removing PID file "%s".' % self.pidfile)

    def start(self, *args, **kw):
        self.log.info('Starting daemon in the background.')
        if is_daemon_running(self.pidfile):
            self.log.error('Daemon already running.')
            raise DaemonAlreadyRunningError(
                'Daemon is already running at %r.' % self.pidfile)
        else:
            self.log.debug('Daemonizing.')
            daemonize(
                self.config.stdredirect,
                self.config.workdir,
                self.config.umask
            )
            self._start(*args, **kw)

    def start_fg(self, *args, **kw):
        self.log.info('Starting daemon in the foreground.')
        self._start(*args, **kw)

    def _start(self, *args, **kw):
        self.log.debug('Starting.')
        create_pidfile(self.pidfile)
        self.log.debug('Created PID File "%s".' % self.pidfile)
        signal.signal(15, self._on_signal_15)
        atexit.register(self._on_exit)
        self.log.debug('Registered signal handlers.')
        self.do_start(*args, **kw)

    def do_stop(self):
        """Stop the daemon"""

    def do_start(self, *args, **kw):
        """Start the daemon"""




