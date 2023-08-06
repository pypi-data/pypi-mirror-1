# -*- coding: utf-8 -*-
from saladedefruits.tests import application
from saladedefruits.saladier import Saladier
from saladedefruits.salade import Salade
from webtest import TestApp
import unittest
import os

dirname = os.path.dirname(__file__)


class SimpleSalade(Salade):
    def __call__(self):
        if self.request.path_info.endswith('.html'):
            self.base_url = '/'.join(self.request.path_url.split('/')[:-1])
        else:
            self.base_url = self.request.path_url
        self.standard_rules()
        self.theme('#content').empty()
        self.theme('#content').append(self.content('body > *'))
        if 'REMOTE_USER' not in self.request.environ:
            self.request.environ['REMOTE_USER'] = 'Anonymous'
        resp = self.get('/user.html')
        self.theme('#content').prepend(resp.doc('#user_infos'))
        self.rewrite_links()
        return self.theme

class Tests(unittest.TestCase):

    def setUp(self):
        self.app = TestApp(Saladier(
                        application,
                        theme=os.path.join(dirname, 'theme.html'),
                        salade=SimpleSalade
                        ))


    def test_index(self):
        resp = self.app.get('/test.html')
        resp.mustcontain('#themed', '<title>Index page</title>', 'Anonymous', 'Welcome')
        assert 'My theme' not in resp, resp

    def test_links(self):
        resp = self.app.get('/test.html')
        resp.mustcontain(
                'http://localhost/test.html#anchor',
                'http://localhost/absolute.html',
                'http://localhost/relative.html',
                'http://localhost/sub/sub.html',
            )

    def test_link_sub_html(self):
        resp = self.app.get('/app/test.html')
        resp.mustcontain(
                'http://localhost/app/test.html#anchor',
                'http://localhost/absolute.html',
                'http://localhost/app/relative.html',
                'http://localhost/app/sub/sub.html',
            )

    def test_hosts(self):
        resp = self.app.get('/app/', extra_environ={'HTTP_HOST':'127.0.0.1:8080', 'SERVER_PORT':'8080'})
        resp.mustcontain('http://127.0.0.1:8080/app/#anchor')

        resp = self.app.get('/app/', extra_environ={'HTTP_HOST':'127.0.0.1:8080', 'HTTP_X_FORWARDED_HOST':'www.gawel.org', 'HTTP_X_FORWARDED_PORT':'443'})
        resp.mustcontain('https://www.gawel.org/app/#anchor')

        resp = self.app.get('/app/', extra_environ={'HTTP_HOST':'127.0.0.1:8080', 'HTTP_X_FORWARDED_HOST':'www.gawel.org', 'HTTP_X_FORWARDED_PORT':'8080'})
        resp.mustcontain('http://www.gawel.org:8080/app/#anchor')

        resp = self.app.get('/app/', extra_environ={'HTTP_HOST':'127.0.0.1:9080', 'SCRIPT_NAME':'/toto',
                                                    'HTTP_X_FORWARDED_HOST':'www.gawel.org', 'HTTP_X_FORWARDED_PORT':'8080'})
        resp.mustcontain('http://www.gawel.org:8080/toto/app/#anchor')

    def test_link_sub_dir(self):
        resp = self.app.get('/app/')
        resp.mustcontain(
                'http://localhost/app/#anchor',
                'http://localhost/absolute.html',
                'http://localhost/app/relative.html',
                'http://localhost/app/sub/sub.html',
            )

    def test_user_index(self):
        resp = self.app.get('/test.html', extra_environ=dict(REMOTE_USER='gawel'))
        resp.mustcontain('#themed', '<title>Index page</title>', 'gawel', 'Welcome')

    def test_static(self):
        resp = self.app.get('/test.js')
        resp.mustcontain('myFunc')

