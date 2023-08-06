
"""
Main runner.
"""

import os, sys, optparse, tempfile, logging

from server import WSGIDaemon, ServerConfig, stop_daemon
from daemon import DaemonAlreadyRunningError, DaemonNotRunningError
from config import Config, Option


# Logging
log = logging.getLogger('wsgid.main')

def init_logging():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

init_logging()


def create_dummy_pidfile():
    fd, filename = tempfile.mkstemp(prefix='wsgid_', suffix='.pid')
    os.close(fd)
    return filename


def stop(conf):
    if not conf.pidfile:
        log.error('Must provide a pidfile to stop.')
        return 1
    else:
        log.info('Stopping daemon with pidfile %r.' % conf.pidfile)
        try:
            stop_daemon(conf.pidfile)
            log.info('Stopped.')
            return 0
        except DaemonNotRunningError, e:
            log.error(e)


def start(conf):
    if not (conf.application or conf.application_factory):
        log.warning('No application, or application_factory -> Hello World.')

    log.info('Starting server.')
    log.info(' '.join(
        ('%s=%r' % item) for item in
         sorted(conf.items(), lambda i1, i2: cmp(i1[0], i2[0]))
    ))

    if conf.foreground:
        log.info('Foregrounding.')
        if not conf.pidfile:
            conf.pidfile = create_dummy_pidfile()
        daemon = WSGIDaemon(conf)
        starter = daemon.start_fg
    else:
        log.info('Daemonizing.')
        if not conf.pidfile:
            log.error('Must provide a pidfile if daemonizing.')
            return 1
        daemon = WSGIDaemon(conf)
        starter = daemon.start

    try:
        starter(conf)
        log.info('Exited.')
        return 0
    except DaemonAlreadyRunningError, e:
        log.error(e)
        return 1


if hasattr(os, "devnull"):
   REDIRECT_TO = os.devnull
else:
   REDIRECT_TO = "/dev/null"


options = [
    Option('config_file', 'The configuration file', '', 'c'),
    Option('pidfile', 'The PID file', '', 'p'),
    Option('foreground', 'Run the server in the foreground', False, 'f', bool, action='store_true'),
    Option('stop', 'Stop the server.', False, 's', bool, action='store_true'),
    Option('application', 'The WSGI Applciation instance to import', '', 'a'),
    Option('application_factory', 'The WSGI Applciation factory to import',  '', 'A'),
    Option('debug', 'Run in debug mode.', False, 'd', bool, action='store_true'),
    Option('port', 'The port to listen on.', 9090, 'P', int),
    Option('host', 'The host to listen on.', '0.0.0.0', 'H'),
    Option('reloader', 'Use the reloader.', False, 'r', bool, action='store_true'),
    Option('logdir', 'The directory for logs.', os.getcwd(), 'L'),
    Option('stdredirect', 'The file to redirect stdio to.', REDIRECT_TO, 'R'),
    Option('workdir', 'The working directory for the daemon.', os.getcwd(), 'w'),
    Option('umask', 'The umask for the spawned child.', 0, 'U', int),
    Option('servername', 'The server name', '', 'n'),
]



def get_config(argv):
    # we need to do this twice, so we can have the config file
    conf = Config(options, 'WSGID')
    conf.add_from_env()
    conf.add_from_argv(argv)
    config_file = conf.config_file
    if config_file:
        conf = Config(options, 'WSGID')
        conf.add_from_file(config_file)
        conf.add_from_env()
        conf.add_from_argv(argv)
    return conf


def main(argv):
    conf = get_config(argv)

    if conf.debug:
        conf.loglevel = logging.DEBUG
    else:
        conf.loglevel = logging.INFO
    log.setLevel(conf.loglevel)

    if conf.stop:
        return stop(conf)
    else:
        return start(conf)


if __name__ == '__main__':
    sys.exit(main(sys.argv))

