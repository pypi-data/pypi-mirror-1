import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from threading import Thread
import socket
#socket.setdefaulttimeout(20)

class ReqHandler(SimpleHTTPRequestHandler):
     def do_GET(self):
         self.end_headers()
         self.send_response(200, '\n\n<html><body><pre>%s</pre></body></html>' % self.headers)

class MyServer(BaseHTTPServer.HTTPServer):

    def serve_forever(self):
        self.running = 1
        while self.running:
            self.handle_request()
        print "STOPPING HTTP SERVER"

    def stop(self):
        self.running = 0
        self.socket.shutdown(socket.SHUT_RDWR)

def launch_servers(test):
     test.globs['httpds'].append(MyServer(('', 45675,) , ReqHandler))
     test.globs['httpds'].append(MyServer(('', 45676,) , ReqHandler))
     test.globs['httpds'].append(MyServer(('', 45677,) , ReqHandler))
     test.globs['httpds'].append(MyServer(('', 45678,) , ReqHandler))
     test.globs['httpds'].append(MyServer(('', 45679,) , ReqHandler))
     for item in test.globs['httpds']:
         t = Thread(target=item.serve_forever)
         t.setDaemon(True)
         t.start()
         test.globs['threads'].append(t)

def stop_servers(test):
    for t in test.globs['httpds']:
        t.stop()
    for t in test.globs['threads']:
        t.join()


