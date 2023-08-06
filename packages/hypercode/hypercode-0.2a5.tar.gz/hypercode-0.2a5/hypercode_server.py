import web
import sys

from urllib2 import urlopen, Request

import hypercode

__version__ = "0.1"

headers = {
    'Accept': 'text/python',
    'User-agent': '%s-%s (eikeon@eikeon.com)' % (__name__, __version__)
    }

urls = (
    '/(.+).py$',    'PythonPage',
    '/(.+).rdf$',    'RDFPage',
    '/(.+)/$',    'HTMLPage',
    '/(.+)$',       'IdPage',
)

def get_uri(path):
    # TODO: is there a better way to get the requested URL
    path = path.replace(".py", "", 1) # TODO
    path = path.replace(".rdf", "", 1) # TODO
    if path.endswith("/"):
        path = path[:-1]
    scheme = web.ctx.environ["wsgi.url_scheme"]
    logical = "%s://%s%s" % (scheme, web.ctx.host, path)
    return logical


class IdPage:
    def GET(self, name):
        try:
            logical = get_uri(web.ctx.path)
            g = hypercode.rdf(logical)
        except Exception, e:
            web.notfound()
        else:
            # TODO better conneg handling
            accept = web.ctx.environ['HTTP_ACCEPT'] 
            if 'application/rdf+xml' in accept:
                name += '.rdf' 
            elif 'text/python' in accept:
                name += '.py' 
            elif "text/html" in accept:
                name += '/' 
            web.seeother('%s' % name)


class PythonPage: 
    def GET(self, name):
        logical = get_uri(web.ctx.path)
        physical = hypercode.get_physical(logical)
        if physical:
            req = Request(physical, None, headers)
            f = urlopen(req)
            print f.read()
        else:
            web.notfound()


class RDFPage: 
    def GET(self, name):
        logical = get_uri(web.ctx.path)
        g = hypercode.rdf(logical)
        if g:
            web.header('Content-type', 'application/rdf+xml')
            print g.serialize(format="pretty-xml")
        else:
            web.notfound()

class HTMLPage: 
    def GET(self, name):
        from cgi import escape

        logical = get_uri(web.ctx.path)
        g = hypercode.rdf(logical)
        try:
            pass #g = hypercode.rdf(logical)
        except Exception, e:
            print "%r" % e
            g = None
        if g:
            web.header('Content-type', 'text/html')
            #print "<pre>%s</pre>" % escape(g.serialize(format="pretty-xml", max_depth=10))
            print "<pre>%s</pre>" % escape(g.serialize(format="n3"))
        else:
            web.notfound()



def main():
    # TODO: how to specify host to listen on:
    # server_address=("localhost", 8080)
    web.run(urls, globals())    

if __name__ == '__main__':
    hypercode.map("http://localhost:8080/engine", "engine.py")
    hypercode.map("http://localhost:8080/handlers", "handlers.py")
    main()

