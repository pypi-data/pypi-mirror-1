# -*- coding: utf-8 -*-
from utils import Request

def join(base, *parts):
    if not base.endswith('/'):
        base += '/'
    return base + '/'.join(parts)

class Salade(object):
    """You must surclasse this classe to apply your own rules:

    .. code-block:: python

        >>> class MySalade(Salade):
        ...     def remove_useless(self):
        ...         self.content('.useless').remove()
        ...     def __call__(self):
        ...         self.standard_rules()
        ...         self.remove_useless()
        ...         return self.theme

    """

    def __init__(self, content, theme, request, response, **config):
        """content and theme ar PyQuery objects. request and response are WebOb objects"""
        self.content = content
        self.theme = theme
        self.request = request
        self.response = response
        self.config = config
        self.base_url = None

    def set_base_url(self, url):
        """define the base_url to rewrite links. You can add something like
        this to your `__call__` method:

        .. sourcecode:: python

            def __call__(self, environ):
                if self.request.path_info.endswith('.html'):
                    self.set_base_url('/'.join(self.request.path_url.split('/')[:-1]))
                else:
                    self.set_base_url(self.request.path_url)
                ...

        if base_url is not set the Salade will use the request.path_url as base_url.
        """
        self.base_url = url

    def rewrite_links(self):
        """rewrite links regarding the current request and the base_url defined in Salade"""
        host_url = self.request.host_url
        path_url = self.request.path_url
        base_url = self.base_url or self.request.path_url
        def link_repl(link):
            if link.startswith('http://') or link.startswith('https://'):
                return link
            elif link.startswith('/_salade/'):
                return self.config['script_name'] + link
            elif link.startswith('/'):
                return join(host_url, link.lstrip('/'))
            elif link.startswith("#"):
                return path_url + link
            return join(base_url, link)
        self.theme[0].rewrite_links(link_repl)

    def standard_rules(self):
        """Apply some common rules on <head />"""
        c_head = self.content('head')
        t_head = self.theme('head')
        t_head.remove('title')
        t_head.prepend(c_head('title'))
        t_head.prepend(c_head('style'))
        t_head.prepend(c_head('link'))
        t_head.prepend(c_head('script'))

    def get(self, url):
        """get an html page from the app or an url"""
        req = Request(self.request.environ.copy())
        req.remove_conditional_headers()
        if url.startswith('/'):
            req.path_info = url
            resp = req.get_response(self.config['application'])
        else:
            resp = Response()
        if resp.content_type.startswith('text/html') and resp.status.startswith('200'):
            return resp
        return None

    def __call__(self, environ):
        """main method. you need to surclass this and apply your own rules. Default is:

        .. sourcecode:: python

            def __call__(self, environ):
                self.standard_rules()
                self.rewrite_links()
                return self.theme

        """
        self.standard_rules()
        self.rewrite_links()
        return self.theme


