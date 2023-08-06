
import os, sys, subprocess

from wsgid.server import BaseWSGIServer, get_app, create_config

from spawning.spawning_controller import run_controller, DEFAULTS

class ConfigHolder(object):
    """A config holder"""
    app = None


class WSGIServer(BaseWSGIServer):

    def start(self):
        if not self.conf.application:
            self.log.warn('For spawning, must provide an importable app instance')
            self.conf.application = 'wsgid.server.default_app'
        factory_args = DEFAULTS.copy()
        factory_args.update({
            'verbose': False,
            'host': self.conf.host,
            'port': self.conf.port,
            'access_log_file': os.path.join(self.conf.logdir, 'access.log'),
            'coverage': False,
            'args': [self.conf.application],
            'wsgid_conf': self.conf.to_dict(),
            'num_processes': 4,
        })

        run_controller('wsgid.servers.spawningweb.config_factory',
                       factory_args)


def config_factory(args):
    args['app_factory'] = 'wsgid.servers.spawningweb.app_factory'
    return args


def app_factory(args):
    conf = create_config(args.get('wsgid_conf', {}))
    app = get_app(conf)
    return app



