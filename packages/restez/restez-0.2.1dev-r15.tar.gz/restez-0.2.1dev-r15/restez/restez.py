# encoding: utf-8

'''restez - A RESTful HTTP command line client.

Based on code from python-rest-client by Benjamin O'Steen.
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2008-2009. All rights reserved.'
__license__ = 'GPL http://www.gnu.org/licenses/gpl.txt'
__id__ = '$Id: restez.py 15 2009-03-30 01:32:29Z miles.chris $'
__url__ = '$URL: https://restez.googlecode.com/svn/trunk/restez/restez.py $'
__version__ = '0.2.1'


# ---- Imports ----

# - Python Modules -
import httplib
import optparse
import os
import pydoc
import sys

from httpconn import HTTPConnection

# ---- Classes ----

class HTTP_BASE(object):
    def __init__(self, options, parser, input_filenames):
        self.headers = {}
        self.filename = None    # read filename into request body
        self.stdin = False      # read stdin into request body
        self.params = []        # request params; list of (key,value) tuples
        
        # User defined "accept" header
        if options.accept:
            self.headers['accept'] = options.accept
        
        # User defined headers
        for head in options.headers:
            try:
                hname, hvalue = head.split(':', 1)
            except:
                parser.error("Invalid header value '%s'. Should be 'headername:value'.")
            self.headers[hname.strip()] = hvalue.strip()
        
        # User defined parameters to add to URL (GET) or body (POST)
        if options.param:
            if not self._allow_params:
                parser.error("This method does not allow params to be specified.")
            else:
                self.params = [tuple(p.split('=', 1)) for p in options.param]
            # elif self._allow_params == 'url':
            #     self.params = dict([tuple(p.split('=', 1)) for p in options.param])
            # elif self._allow_params == 'body':
            #     self.body = urllib.urlencode([tuple(p.split('=', 1)) for p in options.param])
            #     if not self.headers.get('content-type'):
            #         self.headers['content-type'] = 'application/x-www-form-urlencoded'
            # else:
            #     raise ValueError("Invalid value for self._allow_params: '%s'" %self._allow_params)
        
        if input_filenames:
            if not self._allow_request_body:
                parser.error("Request body not allowed for this method.")
            
            # TODO: support multiple input files
            if len(input_filenames) > 1:
                sys.stderr.write("Warning: Reading from multiple files has not yet been implemented. Only first filename used.\n")
            filename = input_filenames[0]
            if filename == '-':
                self.stdin = True
            else:
                self.filename = filename
    
    def send_request(self, uri, auth=None):
        """
        
        auth : tuple containing two strings (username, password)
        """
        kwargs = dict(
            logger=output,
            user_agent='restez/%s' %__version__,
        )
        if auth:
            if isinstance(auth, tuple) and len(auth) == 2:
                kwargs['username'] = auth[0]
                kwargs['password'] = auth[1]
            else:
                raise ValueError("Expected a 2-tuple of strings for auth, got: %s"%str(auth))
        
        body = None
        
        if not body and self.stdin:
            body = sys.stdin.read()
        
        conn = HTTPConnection(**kwargs)
        response = conn.request(
            method=self._method,
            uri=uri,
            params=self.params,
            body=body,
            filename=self.filename,
            headers=self.headers,
        )
        return response
    

class HTTP_GET(HTTP_BASE):
    _method = 'get'
    _allow_request_body = False
    _allow_params = True

class HTTP_HEAD(HTTP_BASE):
    _method = 'head'
    _allow_request_body = False
    _allow_params = True

class HTTP_POST(HTTP_BASE):
    _method = 'post'
    _allow_request_body = True
    _allow_params = True

class HTTP_PUT(HTTP_BASE):
    _method = 'put'
    _allow_request_body = True
    _allow_params = True

class HTTP_DELETE(HTTP_BASE):
    _method = 'delete'
    _allow_request_body = False
    _allow_params = True

class HTTP_OPTIONS(HTTP_BASE):
    _method = 'options'
    _allow_request_body = False
    _allow_params = False



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
    parser.add_option('-p', '--param', dest='param', action='append',
        metavar="NAME=VALUE", default=[],
        help="Specify a NAME=VALUE parameter for a POST or GET request. Option can be used multiple times.")
    
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
