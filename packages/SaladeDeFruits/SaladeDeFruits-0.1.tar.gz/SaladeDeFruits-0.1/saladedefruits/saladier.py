# -*- coding: utf-8 -*-
import os
from utils import Request
from lxml.html import tostring
from pyquery import PyQuery
from salade import Salade
from paste.fileapp import FileApp


class Saladier(object):
    """Take your app and a apply a :class:`~saladedefruits.salade.Salade`
    on it if output is html. You must provide an html file as theme. All
    static files found in the theme's directory are available at
    `/_salade/`. salade is a :class:`~saladedefruits.salade.Salade` or a
    path to a class (eg: `mymodule:MySalade`)
    """

    def __init__(self, application, theme=None, salade=None, **config):
        self.application = application
        if os.path.isfile(theme):
            theme = os.path.abspath(theme)
            self.theme_dir = os.path.dirname(theme)
            fd = open(theme, 'rb')
            self.theme = fd.read()
            fd.close()
        else:
            raise IOError('Invalid theme: %s' % theme)

        if isinstance(salade, basestring):
            mod_name, klass_name = skin.split(':')
            mod = __import__(mod_name, globals(), locals(), [''])
            klass = getattr(mod, klass_name, None)
        else:
            klass = salade

        if not isinstance(klass(None, None, None, None), Salade):
            raise ValueError('Invalid parameters "skin" %s' % skin)

        self.salade = klass
        self.config = config

    def __call__(self, environ, start_response):
        req = Request(environ)
        if req.path_info.startswith('/_salade/'):
            sub_path = req.path_info[9:]
            filename = os.path.join(self.theme_dir, sub_path)
            if os.path.isfile(filename):
                return FileApp(filename)(environ, start_response)
            else:
                raise IOError(filename)
        resp = req.get_response(self.application)
        if resp.content_type and resp.content_type.startswith('text/html'):
            theme = PyQuery(self.theme)
            config = self.config.copy()
            config.update(application=self.application)
            body = self.salade(resp.doc, theme, req, resp, **config)()
            if isinstance(body, str):
                resp.body = body
            else:
                resp.doc = body
        return resp(environ, start_response)


def make_salade(app, global_config, **local_config):
    """Paste entry point:

    .. code-block:: ini

        [filter:skin]
        use = egg:SaladeDeFruits
        theme = %(here)s/static/theme.html
        salade = mymodule:MySalade

    """
    return Saladier(app, **local_config)

