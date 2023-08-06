# encoding: utf-8

'''http_test_server
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2009. All rights reserved.'
__id__ = '$Id: http_test_server.py 18 2009-07-14 07:29:00Z miles.chris $'
__url__ = '$URL: https://restez.googlecode.com/svn/trunk/tests/http_test_server.py $'


# ---- Imports ----

# - Python modules -
import base64
import BaseHTTPServer
import os


# ---- Classes ----

class HTTPTestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_response()
    
    def do_HEAD(self):
        self.handle_response(body=False)
    
    def do_POST(self):
        self.handle_response()
    
    def do_PUT(self):
        self.handle_response()
    
    def do_DELETE(self):
        self.handle_response()
    
    def handle_response(self, body=True):
        if self.path == "/user_agent":
            response = self.user_agent_response()
        elif self.path == "/test_auth":
            response = self.test_auth_response()
        else:
            # All other paths
            response = self.info_response()
        
        self.send_response(200, self.responses[200][0])
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        
        # if body and response:
        if body:
            self.wfile.write(response)
    
    def info_response(self):
        fields = dict(
            command = self.command,
            client_ip = self.client_address[0],
            path = self.path,
            request_version = self.request_version,
        )
        return "%(client_ip)s %(command)s %(path)s %(request_version)s" %fields
    
    def user_agent_response(self):
        user_agent = self.headers.get("User-Agent", "")
        return "%s" %user_agent
    
    def test_auth_response(self):
        response = username = password = ''
        auth = self.headers.get('authorization', '')
        if auth.startswith('Basic '):
            username,password = base64.decodestring(auth[6:]).split(':')
            response = "Basic %s:%s" %(username,password)
        return response.strip()
    
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

    
