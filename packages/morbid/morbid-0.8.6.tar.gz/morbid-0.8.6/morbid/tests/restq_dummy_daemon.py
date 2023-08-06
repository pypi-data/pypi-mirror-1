from twisted.web import server, resource
from twisted.internet import reactor
import time
try:
    try:
        import json
    except ImportError:
        try:
            import cjson as json
        except ImportError:
            try:
                import simplejson as json
            except ImportError:
                import demjson as json
except ImportError:
    raise ImportError, "Could not load one of: Python json, cjson, simplejson, demjson. Please install a json module."
if hasattr(json, 'encode'):
    encode = json.encode
    decode = json.decode
elif hasattr(json, 'dumps'):
    encode = json.dumps
    decode = json.loads
elif hasattr(json, 'write'):
    encode = json.write
    decode = json.read
else:
    raise ImportError, 'Fatal Error: loaded unknown json module: "%s".'%(json.__file__,)

PORT = 5000
cbUrls = {
    'connect':'http://localhost:%s/connect'%PORT,
    'disconnect':'http://localhost:%s/disconnect'%PORT,
    'subscribe':'http://localhost:%s/subscribe'%PORT,
    'unsubscribe':'http://localhost:%s/unsubscribe'%PORT,
    'send':'http://localhost:%s/send'%PORT,
}

class DummyLeaf(object):
    def __init__(self, data):
        self.data = data

    def render(self, request):
        return self.data

def wrap(data):
    print "sending data:",data
    return DummyLeaf(encode(data))

class RestQDummyResource(resource.Resource):
    def getChild(self, path, request):
        if not path or path == "/":
            return wrap(cbUrls)
        headers = decode(request.content.read())
        print '-------------------'
        print 'headers:',headers
        username = headers['username']
        destination = headers.get("destination",None)
        if path in cbUrls:
            print 'checking path: "%s"'%(path,)
            if path == "connect":
                if username == "noconnect":
                    return wrap({"allow":"no"})
            elif path == "send":
                newBody = "the server has modified this message:" + headers['body']
                if username == 'nosend':
                    return wrap({"allow":"no"})
                elif username == 'slow':
                    time.sleep(1)
                return wrap({"body":newBody})
            elif path == "subscribe":
                if destination == "auto":
                    return wrap({"autosubscribe":["room1","room2","room3"]})
            elif path == "unsubscribe":
                if destination == "auto":
                    return wrap({"autounsubscribe":["room1","room2","room3"]})
            return wrap({})

if __name__ == "__main__":
    site = server.Site(RestQDummyResource())
    print 'running on %s'%PORT
    reactor.listenTCP(PORT, site)
    reactor.run()