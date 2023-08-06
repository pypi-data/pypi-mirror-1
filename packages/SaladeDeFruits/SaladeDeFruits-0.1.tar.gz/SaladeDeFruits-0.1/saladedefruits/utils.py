# -*- coding: utf-8 -*-
from pyquery import PyQuery
from lxml.html import tostring
import webob

class Response(webob.Response):

    def _get__doc(self):
        return PyQuery(self.body)

    def _set__doc(self, value):
        self.body = tostring(value[0])

    doc = property(_get__doc, _set__doc)

class Request(webob.Request):
    ResponseClass = Response

