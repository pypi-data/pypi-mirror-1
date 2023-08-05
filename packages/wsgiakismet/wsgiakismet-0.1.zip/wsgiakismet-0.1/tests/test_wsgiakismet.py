#! /usr/bin/env python

# Copyright (c) 2006 L. C. Rees.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 3.  Neither the name of the Portable Site Information Project nor the names
# of its contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import unittest
import wsgiakismet
from StringIO import StringIO 
from urllib import urlencode

# Put valid Wordpress API key here to test
key = ''
blog = 'http://www.example.com/'


class TestWsgiAkisimet(unittest.TestCase):

    def dummy_sr(self, status, headers, exc_info=None):
        pass

    def test_negative(self):
        env = {
        'HTTP_METHOD':'POST',
        'wsgi.input':StringIO(''),
        'QUERY_STRING':urlencode({'comment_author':'Bob Saunders',
            'comment_author_email':'bob@saunders.net', 'comment_author_url':'',
            'comment':'The post was informative.'}),
        'REMOTE_ADDR':'207.89.134.5',
        'HTTP_USER_AGENT':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; YPC 3.0.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)'
        }
        @wsgiakismet.akismet(key, blog)
        def test(environ, start_response):
            start_response('200 OK', [('Content-type', 'text/plain')])
            return ['Good']
        response = test(env, self.dummy_sr)
        self.assertEqual(response[0], 'Good')

    def test_positive(self):
        env = {
        'HTTP_METHOD':'POST',
        'wsgi.input':StringIO(''),
        'QUERY_STRING':urlencode({'comment_author':'viagra-test-123',
            'comment_author_email':'viagra@viagraoffer.net', 'comment_author_url':'',
            'comment':'VIAGRA! LOTS OF VIAGRA!'}),
        'REMOTE_ADDR':'10.9.4.59',
        'HTTP_USER_AGENT':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; YPC 3.0.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)'
        }
        @wsgiakismet.akismet(key, blog)
        def test(environ, start_response):
            start_response('200 OK', [('Content-type', 'text/plain')])
            return ['Good']
        response = test(env, self.dummy_sr)
        self.assertEqual(response[0], 'Comment was spam.')          


if __name__ == '__main__': unittest.main()
       