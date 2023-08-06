

from wsgid.server import BaseWSGIServer

import fapws._evwsgi as evwsgi
from fapws import base

class WSGIServer(BaseWSGIServer):

    name = 'fapws3'

    def start(self):
        evwsgi.start(self.conf.host, self.conf.port)
        evwsgi.set_base_module(base)
        evwsgi.wsgi_cb(('', self.app))
        self.log.info('Starting Fapws3 web server')
        #evwsgi.set_debug(0)
        evwsgi.run()

    def stop(self):
        pass



