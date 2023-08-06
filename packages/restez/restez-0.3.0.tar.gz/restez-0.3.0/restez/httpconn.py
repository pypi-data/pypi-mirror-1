# encoding: utf-8

'''httpconn - A HTTP client library.

(Some parts originally based on code from python-rest-client by
Benjamin O'Steen. Much of that has been modified or re-written.)
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2008-2009. All rights reserved.'
__license__ = 'GPL http://www.gnu.org/licenses/gpl.txt'
__id__ = '$Id: httpconn.py 24 2009-09-08 02:16:37Z miles.chris $'
__url__ = '$URL: https://restez.googlecode.com/svn/trunk/restez/httpconn.py $'


# ---- Imports ----

# - Python modules -
import base64
import httplib
import mimetypes
import sys
import urllib
from urlparse import urlsplit, urljoin


# ---- Classes ----

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
    def __init__(self, base_uri=None, username=None, password=None, user_agent=None, logger=None):
        
        if base_uri is None:
            self.base_uri = None
        else:
            self.base_uri = urlsplit(base_uri)
        
        self.username = username
        self.password = password
        
        if logger is not None:
            assert callable(logger), "Value of logger must be a callable; instead got: %s"%logger
        self.logger = logger
        
        if user_agent is None:
            self.user_agent = "Python/%s"%sys.version.split()[0]
        else:
            self.user_agent = user_agent
    
    def log(self, *args, **kwargs):
        if self.logger:
            self.logger(*args, **kwargs)
    
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
    
    def request(self, method="get", uri=None, params=None, body=None, filename=None, headers={}):
        req_headers = {}
        req_headers.update(headers)
        
        uri = self.build_uri(uri)
        if uri is None:
            raise ValueError("No uri is specified")
        
        method = method.lower()
        
        req_headers['User-Agent'] = self.user_agent
        
        BOUNDARY = u'00hoYUXOnLD5RQ8SKGYVgLLt64jejnMwtO7q8XE1'
        CRLF = u'\r\n'
        
        if filename and body:
            fn = open(filename ,'r')
            chunks = fn.read()
            fn.close()
            
            # Attempt to find the Mimetype
            content_type = self.get_content_type(filename)
            req_headers['Content-Type']='multipart/form-data; boundary='+BOUNDARY
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
            req_headers['Content-Length'] = str(len(body))
        
        elif body:
            if not req_headers.get('Content-Type', None):
                req_headers['Content-Type'] = 'application/octet-stream'
            req_headers['Content-Length'] = str(len(body))
        
        elif filename:
            fn = open(filename ,'r')
            body = fn.read()
            fn.close()
            if not req_headers.has_key('Content-Type'):
                req_headers['Content-Type'] = self.get_content_type(filename)
            req_headers['Content-Length'] = str(len(body))
        
        else:
            # if req_headers.has_key('Content-Length'):
            #     del req_headers['Content-Length']
            # 
            # req_headers['Content-Type'] = 'text/plain'
            
            if params:
                if method in ("get", "head", "delete"):
                    uri += u"?" + urllib.urlencode(params)
                elif method in ("put", "post"):
                    req_headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    body = urllib.urlencode(params)
        
        urlparts = urlsplit(uri)
        if urlparts.scheme == 'https':
            httpconn = httplib.HTTPSConnection(urlparts.netloc)
        else:
            httpconn = httplib.HTTPConnection(urlparts.netloc)
        req_headers.update(self.add_basic_auth_credentials())
        
        self.log("Sending %s request to %s", method.upper(), uri)
        self.log("\nRequest headers include:")
        for k,v in req_headers.items():
            self.log(" %s: %s", k, v)
        
        path = urlparts.path
        if urlparts.query:
            path += '?' + urlparts.query
        httpconn.request(method.upper(), path, body, req_headers)
        response = httpconn.getresponse()
        result = {
            u'headers': dict(response.getheaders()),
            u'body': response.read(),
            u'status': response.status,
            u'reason': response.reason,
        }
        httpconn.close()
        
        return result
    

