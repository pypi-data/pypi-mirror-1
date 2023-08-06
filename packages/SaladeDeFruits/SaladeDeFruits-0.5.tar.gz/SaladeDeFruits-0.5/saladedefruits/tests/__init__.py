# -*- coding: utf-8 -*-
from webob import Request, Response
import os

dirname = os.path.dirname(__file__)

def application(environ, start_response):
    req = Request(environ)
    resp = Response()
    filename = os.path.join(dirname, req.path_info.split('/')[-1])
    if not os.path.isfile(filename):
        filename = os.path.join(dirname, 'test.html')
    dummy, ext = os.path.splitext(filename)
    if ext in ('.html',):
        resp.content_type = 'text/html; charset=utf-8'
    if ext in ('.css',):
        resp.content_type = 'text/css; charset=utf-8'
    if ext in ('.js',):
        resp.content_type = 'text/javascript; charset=utf-8'
    if ext in ('.png',):
        resp.content_type = 'image/jpeg'
    body = open(filename, 'rb').read()
    resp.body = body % req.environ
    return resp(environ, start_response)
