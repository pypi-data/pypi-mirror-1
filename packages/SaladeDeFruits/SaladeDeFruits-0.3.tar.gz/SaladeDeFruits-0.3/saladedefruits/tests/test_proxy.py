# -*- coding: utf-8 -*-
from saladedefruits.proxy import Proxy
from webtest import TestApp
import unittest

class TestProxy(unittest.TestCase):
    href = 'http://www.gawel.org/'

    def setUp(self):
        self.app = TestApp(Proxy(self.href, rewrite_links=True, strip_script_name=False))

    def test_rewrite(self):
        resp = self.app.get('/stream', extra_environ=dict(REMOTE_ADDR='localhost'))
        resp.mustcontain('http://localhost/stream/"')

    def test_rewrite_with_prefix(self):
        resp = self.app.get('/', extra_environ=dict(REMOTE_ADDR='localhost', SCRIPT_NAME='/stream'))
        resp.mustcontain('http://localhost/stream/stream/"', '<![CDATA[')

class TestProxy2(unittest.TestCase):
    href = 'http://www.gawel.org/stream'

    def setUp(self):
        self.app = TestApp(Proxy(self.href, rewrite_links=True, strip_script_name=True))

    def test_rewrite(self):
        resp = self.app.get('/', extra_environ=dict(REMOTE_ADDR='localhost', SCRIPT_NAME='/stream'))
        resp.mustcontain('http://localhost/stream/"')

