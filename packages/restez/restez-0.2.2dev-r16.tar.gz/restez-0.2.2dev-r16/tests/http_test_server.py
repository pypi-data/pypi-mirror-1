# encoding: utf-8

'''http_test_server
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2009. All rights reserved.'
__id__ = '$Id: http_test_server.py 5 2009-01-08 14:26:49Z miles.chris $'
__url__ = '$URL: https://restez.googlecode.com/svn/trunk/tests/http_test_server.py $'


# ---- Imports ----

# - Python modules -
import BaseHTTPServer
import os


# ---- Classes ----

class HTTPTestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.info_response()
    
    def do_HEAD(self):
        self.info_response(body=False)
    
    def do_POST(self):
        self.info_response()
    
    def do_PUT(self):
        self.info_response()
    
    def do_DELETE(self):
        self.info_response()
    
    def info_response(self, body=True):
        response = ''
        if body:
            fields = dict(
                command = self.command,
                client_ip = self.client_address[0],
                path = self.path,
                request_version = self.request_version,
            )
            response = "%(client_ip)s %(command)s %(path)s %(request_version)s" %fields
        
        self.send_response(200, self.responses[200][0])
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        
        if response:
            self.wfile.write(response)
        
    def log_request(self, *args, **kwargs):
        # no access logging thanks
        pass
    


# ---- Functions ----

def create_http_server(bind_address='0.0.0.0', bind_port=0, handler=HTTPTestHandler):
    """Create a HTTP server using handler to process requests.  By default the
    server will bind to a random free TCP port chosen by the system.
    Examine httpd.server_address to find out what port was used.
    
    Returns a BaseHTTPServer.HTTPServer object.
    
    Use httpd.serve_forever() to start the server.
    """
    server_address = ('127.0.0.1', 0)   # localhost; let server choose a free TCP port
    httpd = BaseHTTPServer.HTTPServer(server_address, handler)
    return httpd

def fork_http_server():
    """Fork a HTTP server process.
    
    Returns a 2-tuple (pid, uri) where pid is the process ID of the
    child HTTP server process; and uri is the base URI of the HTTP
    server.
    """
    httpd = create_http_server()
    uri = "http://%s:%s/" %httpd.server_address
    pid = os.fork()
    if pid == 0:
        # child process
        httpd.serve_forever()
        sys.exit(0)
    
    return pid,uri

    
