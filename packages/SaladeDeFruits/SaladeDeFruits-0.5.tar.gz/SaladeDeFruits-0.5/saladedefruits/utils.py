# -*- coding: utf-8 -*-
from pyquery import PyQuery
from lxml.html import tostring
import webob

class Response(webob.Response):

    def _get__doc(self):
        body = self.body.strip()
        if body and '<?xml version=' not in body:
            body = '<?xml version="1.0" encoding="utf-8"?>' + body
        return PyQuery(body, parser='html')

    def _set__doc(self, value):
        self.body = tostring(value[0])

    doc = property(_get__doc, _set__doc)

class Request(webob.Request):
    ResponseClass = Response

