# -*- coding: utf-8 -*-
from wsgiproxy.exactproxy import proxy_exact_request
import urlparse
from utils import Request

class Proxy(object):
    """This is the equivalent to the deliverance Proxy. eg. you can rewrite
    links and strip script name."""
    def __init__(self, href, rewrite_links=False, strip_script_name=False,**kwargs):
        self.rewrite_links = rewrite_links
        self.strip_script_name = strip_script_name
        self.href_scheme, self.href_netloc, self.href_path, href_query, href_fragment = urlparse.urlsplit(href, 'http')
        if self.href_path.endswith('/'):
            self.href_path = self.href_path.rstrip('/')

    def get_response(self, req):
        if self.strip_script_name:
            script_name = ''
        else:
            script_name = req.script_name
        new_orig_base = '%s://%s%s' % (req.environ['wsgi.url_scheme'],
                                       req.environ['SERVER_NAME'],
                                       script_name
                                      )
        req.environ['SERVER_NAME'] = req.environ['HTTP_HOST'] = self.href_netloc
        req.path_info = self.href_path + req.path_info
        if self.strip_script_name:
            req.script_name = ''
        resp = req.get_response(proxy_exact_request)
        if resp.content_type and resp.content_type.startswith('text/html'):
            if self.rewrite_links:
                doc = resp.doc
                orig_base = '%s://%s' % (req.environ['wsgi.url_scheme'], self.href_netloc)
                def link_repl(link):
                    if link == orig_base:
                        return new_orig_base
                    if link.startswith('/'):
                        return new_orig_base + link
                    if not link.startswith(orig_base):
                        return link
                    return new_orig_base + link[len(orig_base):]
                doc[0].make_links_absolute(orig_base)
                doc[0].rewrite_links(link_repl)
                resp.doc = doc
            return resp
        return resp

    def __call__(self, environ, start_response=None):
        req = Request(environ)
        resp = self.get_response(req)
        return resp(environ, start_response)



def make_proxy(global_config, **local_config):
    href = local_config.pop('href')
    return Proxy(href, **local_config)

