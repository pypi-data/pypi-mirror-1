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
        self.standard_rules()
        self.theme('#content').empty()
        self.theme('#content').append(self.content('body > *'))
        if 'REMOTE_USER' not in self.request.environ:
            self.request.environ['REMOTE_USER'] = 'Anonymous'
        resp = self.get('/user.html')
        self.theme('#content').prepend(resp.doc('#user_infos'))
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

    def test_user_index(self):
        resp = self.app.get('/test.html', extra_environ=dict(REMOTE_USER='gawel'))
        resp.mustcontain('#themed', '<title>Index page</title>', 'gawel', 'Welcome')

    def test_static(self):
        resp = self.app.get('/test.js')
        resp.mustcontain('myFunc')

