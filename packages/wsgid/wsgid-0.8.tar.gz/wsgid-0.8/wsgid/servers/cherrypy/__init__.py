

from wsgid.server import BaseWSGIServer
from cherryserver import CherryPyWSGIServer


class WSGIServer(CherryPyWSGIServer, BaseWSGIServer):

    name = 'cherrypy'

    def __init__(self, conf, app):
        BaseWSGIServer.__init__(self, conf, app)
        CherryPyWSGIServer.__init__(self,
            (conf.host, conf.port),
            app,
            server_name = conf.servername
        )

    def start(self):
        CherryPyWSGIServer.start(self)

