
from werkzeug.serving import run_simple

from wsgid.server import BaseWSGIServer

class WSGIServer(BaseWSGIServer):
    name = 'Werkzeug'

    def start(self):
        run_simple(self.conf.host, self.conf.port, self.app, processes=1)


