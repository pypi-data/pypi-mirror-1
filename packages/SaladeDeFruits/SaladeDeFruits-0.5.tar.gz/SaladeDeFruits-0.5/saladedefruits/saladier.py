# -*- coding: utf-8 -*-
import os
import urlparse
from utils import Request, Response
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

    def __init__(self, application, theme=None, salade=None, root_url=None, **config):
        self.application = application
        self.root_url = root_url
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

    def get(self, url):
        """get an html page from the app or an url"""
        if url.startswith('/'):
            req = Request.blank(url)
            resp = req.get_response(self.application)
        else:
            resp = Response()
        if resp.content_type.startswith('text/html') and resp.status.startswith('200'):
            return resp
        return None

    def __call__(self, environ, start_response):
        req = Request(environ)
        if req.path_info.startswith('/_salade/'):
            sub_path = req.path_info[9:]
            filename = os.path.join(self.theme_dir, sub_path)
            if os.path.isfile(filename):
                return FileApp(filename)(environ, start_response)
            else:
                raise IOError(filename)

        if self.root_url:
            scheme, host = urlparse.urlparse(self.root_url)
            if ':' in host:
                host, port = host.split(':')
            else:
                port = scheme == 'https' and '443' or '80'
        elif 'HTTP_X_FORWARDED_HOST' in req.environ:
            host = req.environ.pop('HTTP_X_FORWARDED_HOST').split(':')[0]
            if 'HTTP_X_FORWARDED_PROTO' in req.environ:
                req.scheme = req.environ.pop('HTTP_X_FORWARDED_PROTO')
            if 'HTTP_X_FORWARDED_SCHEME' in req.environ:
                req.scheme = req.environ.pop('HTTP_X_FORWARDED_SCHEME')
            if 'HTTP_X_FORWARDED_PORT' in req.environ:
                port = req.environ.pop('HTTP_X_FORWARDED_PORT')
            else:
                port = req.scheme == 'https' and '443' or '80'
        else:
            host = req.host
            if ':' in host:
                host, port = host.split(':')
            else:
                port = '80'


        req.environ['SERVER_NAME'] = host
        req.environ['SERVER_PORT'] = str(port)
        if 'HTTP_HOST' in req.environ:
            del req.environ['HTTP_HOST']
        if port == '443':
            req.scheme = 'https'

        if 'HTTP_X_FORWARDED_PATH' in req.environ:
            req.script_name = req.environ['HTTP_X_FORWARDED_PATH']

        config = self.config.copy()
        config.update(script_name=req.script_name)
        resp = req.get_response(self.application)
        status = resp.status[0]
        if resp.content_type and resp.content_type.startswith('text/html') and status in '245':
            theme = PyQuery(self.theme, parser='html')
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

