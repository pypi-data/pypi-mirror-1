

from twisted.internet import reactor
from twisted.web import server
from twisted.web.wsgi import WSGIResource
from twisted.python.threadpool import ThreadPool
from twisted.internet import reactor

from wsgid.server import BaseWSGIServer

# Create and start a thread pool,
wsgiThreadPool = ThreadPool()
wsgiThreadPool.start()

# ensuring that it will be stopped when the reactor shuts down
reactor.addSystemEventTrigger('after', 'shutdown', wsgiThreadPool.stop)

# Create the WSGI resource

class WSGIServer(BaseWSGIServer):

    def start(self):
        self.log.info('Starting Twisted web server.')
        wsgi_res = WSGIResource(reactor, wsgiThreadPool, self.app)
        site = server.Site(wsgi_res)
        reactor.listenTCP(self.conf.port, site)
        reactor.run()

    def stop(self):
        self.log.debug('Stopping Twisted web server.')
        reactor.stop()


