# -*- coding: utf-8 -*-
from utils import Request

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

    def standard_rules(self):
        """Apply some common rules on <head />"""
        c_head = self.content('head')
        t_head = self.theme('head')
        t_head.remove('title')
        t_head.prepend(c_head('title'))
        t_head.prepend(c_head('style'))
        t_head.prepend(c_head('link'))

    def get(self, url):
        """get an html page from the app or an url"""
        req = Request(self.request.environ)
        req.remove_conditional_headers()
        if url.startswith('/'):
            req.path_info = url
            resp = req.get_response(self.config['application'])
        if resp.content_type.startswith('text/html') and resp.status.startswith('200'):
            return resp
        return None

    def __call__(self, environ):
        """main method. you need to surclass this and apply your own rules"""
        self.standard_rules()
        return self.theme


