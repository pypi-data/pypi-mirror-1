
"""
Main runner.
"""

import os, sys

from daemon import DaemonAlreadyRunningError, DaemonNotRunningError, \
    WSGIDaemon, stop_daemon, create_logger
from config import Config, Option


def stop(conf):
    log = create_logger(conf, 'stopper')
    if not conf.pidfile:
        log.error('Need a pidfile to stop.')
        return 1
    else:
        try:
            stop_daemon(conf.pidfile)
            log.info('Stopped %r' % conf.pidfile)
            return 0
        except DaemonNotRunningError, e:
            log.error('No running daemon for %r' % conf.pidfile)
            return 1


def start(conf):
    daemon = WSGIDaemon(conf)
    daemon.start()

servers = 'cherrypy (default), twistedweb, circuitsweb, fapws3, spawningweb, wz'

options = [
    Option('config_file', 'The configuration file', '', 'c'),
    Option('pidfile', 'The PID file', '', 'p'),
    Option('stop', 'Stop the server.', False, 's', bool, action='store_true'),
    Option('application', 'The WSGI Applciation instance to import', '', 'a'),
    Option('application_factory', 'The WSGI Applciation factory to import',  '', 'A'),
    Option('debug', 'Run in the werkzeug debugger.', False, 'd', bool, action='store_true'),
    Option('port', 'The port to listen on.', 9090, 'P', int),
    Option('host', 'The host to listen on.', '0.0.0.0', 'H'),
    Option('no_reloader', 'Do not use the reloader.', False, 'N', bool, action='store_true'),
    Option('logdir', 'The directory for logs.', os.path.join(os.getcwd(), 'logs'), 'L'),
    Option('workdir', 'The working directory for the daemon.', os.getcwd(), 'w'),
    Option('servername', 'The server name', '', 'n'),
    Option('ssl_certificate', 'The ssl certificate', '', 'C'),
    Option('ssl_private_key', 'The ssl private key', '', 'K'),
    Option('virtualenv', 'Path to a virtualenv to use', '', 'e'),
    Option('verbose', 'Verbose logging', False,
           'v', bool, action='store_true'),
    Option('no_log_stdout', 'Do not log on stdout', False, 'T', bool,
            action='store_true'),
    Option('server', 'Server type to use. One of: %s' % servers, 'cherrypy', 'O'),
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
    if conf.stop:
        return stop(conf)
    else:
        return start(conf)


if __name__ == '__main__':
    sys.exit(main(sys.argv))

