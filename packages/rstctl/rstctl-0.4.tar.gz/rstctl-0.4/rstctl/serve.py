# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
from random import random
from cStringIO import StringIO
import BaseHTTPServer
import SimpleHTTPServer

def do_GET(self):
    f = StringIO()
    self.send_response(200)
    print >> f, self.value.encode('utf-8')
    self.send_header('Content-Type','text/html;charset=utf-8')
    self.end_headers()
    f.seek(0)
    self.copyfile(f, self.wfile)
    f.close()
    return

SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET = do_GET

def publish(value, browser=True):
        handler=SimpleHTTPServer.SimpleHTTPRequestHandler
        handler.value = value
        httpd = BaseHTTPServer.HTTPServer(('',6969), handler)
        if browser:
            webbrowser.open('http://localhost:6969/%s' % random())
        else:
            print 'Open your browser at http://localhost:6969/'
        try:
            httpd.handle_request()
        except KeyboardInterrupt:
            return

__all__ = ('publish',)

