#!/usr/bin/python
from WebProcessingServer.Server import wsgiApp

import sys

if __name__ == '__main__':
    from wsgiref import simple_server
    from SocketServer import ThreadingMixIn
    class myServer(ThreadingMixIn, simple_server.WSGIServer):
        pass
    print "Starting up Server..."
    httpd = myServer(('',8080), simple_server.WSGIRequestHandler,)
    print "Starting application..."
    httpd.set_app(wsgiApp)
    print "Now listening at http://localhost:8080/"
    httpd.serve_forever()
