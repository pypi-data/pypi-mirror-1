# encoding: utf-8

'''restez

Based on code from python-rest-client by Benjamin O'Steen.
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2008. All rights reserved.'
__license__ = 'GPL http://www.gnu.org/licenses/gpl.txt'
__id__ = '$Id: restez.py 10 2009-02-15 13:40:51Z miles.chris $'
__url__ = '$URL: https://restez.googlecode.com/svn/trunk/restez/restez.py $'
__version__ = '0.1.2'


# ---- Imports ----

# - Python Modules -
import base64
import httplib
import httplib2
import mimetypes
import optparse
import os
import pydoc
import sys
import urllib
from urlparse import urlsplit, urljoin


# ---- Classes ----

class HTTP_BASE(object):
    def __init__(self, options, parser, input_filenames):
        self.headers = {}
        self.filename = None    # read filename into request body
        self.stdin = False      # read stdin into request body
        self.params = {}        # CGI params for GET or PUT
        
        if options.accept:
            self.headers['accept'] = options.accept
        
        if input_filenames:
            if not self._allow_request_body:
                parser.error("Request body not allowed for this method.")
            
            # TODO: support multiple input files
            if len(input_filenames) > 1:
                sys.stderr.write("Reading from multiple files has not yet been implemented. Only first filename used.\n")
            filename = input_filenames[0]
            if filename == '-':
                self.stdin = True
            else:
                self.filename = filename
        
        for head in options.headers:
            try:
                hname, hvalue = head.split(':', 1)
            except:
                parser.error("Invalid header value '%s'. Should be 'headername:value'.")
            self.headers[hname.strip()] = hvalue.strip()
    
    def send_request(self, uri, auth=None):
        """
        
        auth : tuple containing two strings (username, password)
        """
        kwargs = dict()
        if auth:
            if isinstance(auth, tuple) and len(auth) == 2:
                kwargs['username'] = auth[0]
                kwargs['password'] = auth[1]
            else:
                raise ValueError("Expected a 2-tuple of strings for auth, got: %s"%str(auth))
        
        body = None
        # params = {}
        # filename = None
        
        if self.stdin:
            body = sys.stdin.read()
        
        conn = HTTPConnection(**kwargs)
        response = conn.request(method=self._method, uri=uri, args=self.params, body=body, filename=self.filename, headers=self.headers)
        return response
    

class HTTP_GET(HTTP_BASE):
    _method = 'get'
    _allow_request_body = False

class HTTP_HEAD(HTTP_BASE):
    _method = 'head'
    _allow_request_body = False

class HTTP_POST(HTTP_BASE):
    _method = 'post'
    _allow_request_body = True

class HTTP_PUT(HTTP_BASE):
    _method = 'put'
    _allow_request_body = True

class HTTP_DELETE(HTTP_BASE):
    _method = 'delete'
    _allow_request_body = False

class HTTP_OPTIONS(HTTP_BASE):
    _method = 'options'
    _allow_request_body = False


class HTTPConnection(object):
    """Make HTTP requests.
    
    Example 1 - Basic HTTP GET request::
    
        conn = HTTPConnection()
        r = conn.request("get", "http://localhost/")
        print "Response Headers:"
        print r['headers']
        print "Response Body:"
        print r['body']
    
    Example 2 - Multiple PUT requests to resources sharing a common base URI::
    
        conn = HTTPConnection("http://10.2.3.4/thinglibrary/")
        for thing in listofthings:
            resource_path = 'things/%s' %(thing, )
            print conn.build_uri(resource_path)                     # display full URL
            r = conn.request("put", resource_path, body="test")     # send PUT request to resource
            print r['headers']['status']                            # display response status
        
    """
    def __init__(self, base_uri=None, username=None, password=None):
        
        if base_uri is None:
            self.base_uri = None
        else:
            self.base_uri = urlsplit(base_uri)
        
        self.username = username
        self.password = password
        
    
    def add_basic_auth_credentials(self):
        headers = {}
        if self.username is not None or self.password is not None:
            headers['authorization'] = 'Basic ' + base64.encodestring("%s:%s" % (self.username or '', self.password or '')).strip()
        return headers
    
    def get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
    def build_uri(self, uri):
        if uri is None:
            result_uri = self.base_uri.geturl()
        elif self.base_uri is None:
            result_uri = uri
        else:
            result_uri = urljoin(self.base_uri.geturl(), uri)
        return result_uri
    
    def request(self, method="get", uri=None, args=None, body=None, filename=None, headers={}):
        uri = self.build_uri(uri)
        if uri is None:
            raise ValueError("No uri is specified")
        
        params = None
        headers['User-Agent'] = 'restez/%s' %__version__
        
        BOUNDARY = u'00hoYUXOnLD5RQ8SKGYVgLLt64jejnMwtO7q8XE1'
        CRLF = u'\r\n'
        
        if filename and body:
            fn = open(filename ,'r')
            chunks = fn.read()
            fn.close()
            
            # Attempt to find the Mimetype
            content_type = self.get_content_type(filename)
            headers['Content-Type']='multipart/form-data; boundary='+BOUNDARY
            encode_string = StringIO()
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + CRLF)
            encode_string.write(u'Content-Disposition: form-data; name="file"; filename="%s"' % filename)
            encode_string.write(CRLF)
            encode_string.write(chunks)
            encode_string.write(CRLF)
            encode_string.write(u'Content-Type: %s' % content_type + CRLF)
            encode_string.write(CRLF)
            encode_string.write(body)
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + u'--' + CRLF)
            
            body = encode_string.getvalue()
            headers['Content-Length'] = str(len(body))
        
        elif body:
            if not headers.get('Content-Type', None):
                headers['Content-Type'] = 'application/octet-stream'
            headers['Content-Length'] = str(len(body))
        
        elif filename:
            fn = open(filename ,'r')
            body = fn.read()
            fn.close()
            if not headers.has_key('Content-Type'):
                headers['Content-Type'] = self.get_content_type(filename)
            headers['Content-Length'] = str(len(body))
        
        else:
            # if headers.has_key('Content-Length'):
            #     del headers['Content-Length']
            # 
            # headers['Content-Type'] = 'text/plain'
            
            if args:
                if method == "get":
                    # path += u"?" + urllib.urlencode(args)
                    uri += u"?" + urllib.urlencode(args)
                elif method == "put" or method == "post":
                    headers['Content-Type']='application/x-www-form-urlencoded'
                    body = urllib.urlencode(args)
        
        httpconn = httplib2.Http()
        headers.update(self.add_basic_auth_credentials())
        
        output("Sending %s request to %s", method.upper(), uri)
        output("\nRequest headers include (HTTP client library may add more):")
        for k,v in headers.items():
            output(" %s: %s", k, v)
        resp, content = httpconn.request(uri, method.upper(), body=body, headers=headers)
        
        # TODO trust the return encoding type in the decode?
        # return {u'headers':resp, u'body':content.decode('UTF-8')}
        return {u'headers':resp, u'body':content}
    


# ---- Constants ----

HTTP_METHODS = dict(
    DELETE = (HTTP_DELETE, 'Send a DELETE request.'),
    GET = (HTTP_GET, 'Send a GET request.'),
    HEAD = (HTTP_HEAD, 'Send a HEAD request.'),
    OPTIONS = (HTTP_OPTIONS, 'Send an OPTIONS request.'),
    POST = (HTTP_POST, 'Send a POST request; accepts "-p", "-f" and input from stdin.'),
    PUT = (HTTP_PUT, 'Send a PUT request; accepts "-p", "-f" and input from stdin.'),
)


# ---- Functions ----

def help_methods():
    output("HTTP Methods:")
    for k,v in sorted(HTTP_METHODS.items()):
        output("  %-10s : %s", k, v[1])


def output(msg, *args, **kwargs):
    sys.stdout.write(msg%args + '\n')

def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    # define usage and version messages
    usageMsg = "usage: %s [options] HTTP_METHOD URI [filename ...]" % sys.argv[0]
    versionMsg = """%s %s""" % (os.path.basename(argv[0]), __version__)
    description = """If one or more filenames are specified the contents of those
files will be used as the request body (only applicable to POST/PUT requests).
Use '-' instead of a filename to read from stdin.
"""

    # get a parser object and define our options
    parser = optparse.OptionParser(usage=usageMsg, version=versionMsg, description=description)
    
    # Help
    parser.add_option('', '--help-methods', dest='help_methods',
        action='store_true', default=False,
        help="show HTTP methods")
    
    # Switches
    parser.add_option('-v', '--verbose', dest='verbose',
        action='store_true', default=False,
        help="verbose output")
    parser.add_option('-d', '--debug', dest='debug',
        action='store_true', default=False,
        help="debugging output (very verbose)")
    parser.add_option('-q', '--quiet', dest='quiet',
        action='store_true', default=False,
        help="suppress output (excluding errors)")
    
    # Options expecting values
    parser.add_option('-A', '--accept', dest='accept',
        metavar="MEDIATYPES", default=None,
        help="Specify HTTP Accept header value, the MEDIATYPES accepted by client.")
    parser.add_option('-U', '--username', dest='username',
        metavar="USERNAME", default=None,
        help="Specify USERNAME for HTTP auth.")
    parser.add_option('-P', '--password', dest='password',
        metavar="PASSWORD", default=None,
        help="Specify PASSWORD for HTTP auth.")
    parser.add_option('-H', '--header', dest='headers', action='append',
        metavar="HEADER", default=[],
        help="Define a request header as 'headername:value'. Option can be used multiple times.")
    
    # *TODO*
    # parser.add_option('-p', '--params', dest='params',
    #     metavar="PARAMS", default=None,
    #     help="Specify HTTP PARAMS, in format 'key1=val1&key2=val2&key3=val3'.")
    
    # Parse options & arguments
    (options, args) = parser.parse_args()
    
    if options.help_methods:
        help_methods()
        return 0
    
    if len(args) < 1:
        parser.error("HTTP method missing (try --help-methods)")
    
    if len(args) < 2:
        parser.error("URI missing (see --help)")
    
    http_method = args[0].upper()
    uri = args[1]
    input_filenames = args[2:]
    
    method_factory = HTTP_METHODS.get(http_method, [None])[0]
    
    if method_factory is None:
        parser.error("Unknown HTTP method '%s' (try --help-methods)" %http_method)
    
    method = method_factory(options, parser, input_filenames)
    
    if options.username is not None or options.password is not None:
        auth = (options.username or '', options.password or '')
    else:
        auth = None
    
    response = method.send_request(uri, auth)
    output("\nResponse Headers")
    for h,v in response['headers'].items():
        output("  %s: %s", h,v)
    output("")
    
    if response['body']:
        ctype = response['headers'].get('content-type')
        if ctype:
            ctype_display = ", %s" %ctype
        else:
            ctype_display = ""
        while True:
            r = raw_input("Response body (%d bytes%s) [p]pager, [d]isplay, [w]rite to file, [s]kip ? " %(len(response['body']), ctype_display))
        
            if r.lower() == 'p':
                pydoc.pager(response['body'])
            elif r.lower() == 'd':
                sys.stdout.write(response['body'] + '\n')
            elif r.lower() == 'w':
                bodyfile = raw_input(" Filename ? ")
                if bodyfile:
                    open(bodyfile, 'w').write(response['body'])
                    output(" Response body written to '%s'" %bodyfile)
            elif r.lower() == 's':
                break
            else:
                continue
            break
    
    else:
        output("Response body was empty")
    
    # Output response status (with description) if possible
    status = response['headers'].get('status')
    if status is None:
        output("Error: no status returned, possibly bad HTTP response.")
        return 1
    try:
        status = int(status.split(None, 2)[0])
    except:
        output("Error: invalid status \"%s\", possibly bad HTTP response.", status)
        return 1
    if hasattr(httplib, 'responses'):
        description = " (%s)" %httplib.responses.get(status, 'Unknown status')
    else:
        description = ''
    output("\nResponse status: %d%s", status, description)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
