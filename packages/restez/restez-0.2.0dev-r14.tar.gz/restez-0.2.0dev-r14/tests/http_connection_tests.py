#!/usr/bin/env python
# encoding: utf-8
"""
http_connection_tests.py

Created by Chris Miles on 2009-01-07.
Copyright (c) 2009 Chris Miles. All rights reserved.
"""

# ---- Imports ----

# - Python modules -
import os
import signal
import unittest

# - Project modules -
from restez.restez import HTTPConnection
from http_test_server import fork_http_server


# ---- Unit Tests ----

class HTTPConnectionNoBaseURITests(unittest.TestCase):
    def setUp(self):
        self.httpd_pid, self.httpd_uri = fork_http_server()
        self.conn = HTTPConnection()
    
    def tearDown(self):
        os.kill(self.httpd_pid, signal.SIGTERM)
    
    def test_type(self):
        self.failUnlessEqual(type(self.conn), HTTPConnection)
    
    def test_build_uri_no_base(self):
        uri = self.conn.build_uri('http://10.2.3.4:8000/foo')
        self.failUnlessEqual('http://10.2.3.4:8000/foo', uri)
    
    def test_request_get(self):
        r = self.conn.request('get', self.httpd_uri)
        self.failUnlessEqual(r['headers']['status'], '200')
    


class HTTPConnectionBuildURIWithBaseURITests(unittest.TestCase):
    def setUp(self):
        self.conn = HTTPConnection('http://10.2.3.4:8000/foo/')
    
    def test_build_uri_from_empty_str(self):
        uri = self.conn.build_uri('')
        self.failUnlessEqual('http://10.2.3.4:8000/foo/', uri)
    
    def test_build_uri_from_none(self):
        uri = self.conn.build_uri(None)
        self.failUnlessEqual('http://10.2.3.4:8000/foo/', uri)
    
    def test_build_uri_from_sub_path(self):
        uri = self.conn.build_uri('bar')
        self.failUnlessEqual('http://10.2.3.4:8000/foo/bar', uri)
    
    def test_build_uri_from_new_path(self):
        uri = self.conn.build_uri('/bar')
        self.failUnlessEqual('http://10.2.3.4:8000/bar', uri)
    
    def test_build_uri_from_back_path(self):
        uri = self.conn.build_uri('../bar')
        self.failUnlessEqual('http://10.2.3.4:8000/bar', uri)
    

class HTTPConnectionWithBaseURITests(unittest.TestCase):
    def setUp(self):
        self.httpd_pid, self.httpd_uri = fork_http_server()
        self.conn = HTTPConnection(self.httpd_uri + 'foo/')
    
    def tearDown(self):
        os.kill(self.httpd_pid, signal.SIGTERM)
    
    def test_request_get_no_path(self):
        r = self.conn.request('get')
        self.failUnlessEqual(r['headers']['status'], '200')
        self.failUnlessEqual(r['body'].split()[2], '/foo/')
    
    def test_request_get_root(self):
        r = self.conn.request('get', '/')
        self.failUnlessEqual(r['headers']['status'], '200')
        self.failUnlessEqual(r['body'].split()[2], '/')
    
    def test_request_get_relative_path(self):
        r = self.conn.request('get', 'bar/zip')
        self.failUnlessEqual(r['headers']['status'], '200')
        self.failUnlessEqual(r['body'].split()[2], '/foo/bar/zip')
    
    def test_request_get_absolute_path(self):
        r = self.conn.request('get', '/foo/bar')
        self.failUnlessEqual(r['headers']['status'], '200')
        self.failUnlessEqual(r['body'].split()[2], '/foo/bar')
    


if __name__ == '__main__':
    unittest.main()
