

from glashammer.application import make_app
from glashammer.utils import Response

from werkzeug import Response, Request


def do_root(req):
    return Response('hello world')

def do_except(req):
    raise Exception

@Request.application
def app(req):
    print req.path
    if req.path == '/':
        return do_root(req)
    elif req.path == '/except':
        return do_except(req)






