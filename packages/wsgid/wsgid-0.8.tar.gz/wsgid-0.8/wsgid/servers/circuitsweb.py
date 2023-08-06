
from wsgid.server import BaseWSGIServer


from circuits.web import BaseServer, wsgi
from circuits.core.workers import cpus, processes
from circuits.net.pollers import EPoll, Poll, Select


class WSGIServer(BaseWSGIServer):
    name = 'circuitsweb'

    def start(self):
        self.server = BaseServer(self.conf.port, poller=Select)
        self.server += wsgi.Gateway(self.app)
        for i in xrange(cpus() - 1):
            self.server.start(process=True)
        self.server.run()

    def stop(self):
        self.server.stop()
        for p in processes():
            p.terminate()


