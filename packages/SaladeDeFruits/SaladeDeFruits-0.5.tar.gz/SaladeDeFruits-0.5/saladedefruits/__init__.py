# -*- coding: utf-8 -*-
from saladier import Saladier
from salade import Salade
__doc__ = """
..
  >>> import tempfile, os, shutil; dirname = tempfile.mkdtemp()

Create your salade::

  >>> from saladedefruits import Salade
  >>> class MySalade(Salade):
  ...     def __call__(self):
  ...         self.standard_rules()
  ...         self.theme('#content').append(self.content('body > *'))
  ...         self.rewrite_links()
  ...         return self.theme


Create a theme::

  >>> filename = os.path.join(dirname, 'theme.html')
  >>> open(filename, 'w').write('''<html>
  ... <head>
  ...   <link type="text/css" rel="stylesheet" href="http://localhost/_salade/style.css"/>
  ... </head>
  ... <body>
  ...   <h1>SaladeDeFruits mixing</h1>
  ...   <div id="content"></div>
  ... </body>''')

Then you need a wsgi application to skin::

  >>> from webob import Response
  >>> def application(environ, start_response):
  ...     resp = Response()
  ...     resp.body = '''<html>
  ...       <head>
  ...         <title>Hello world</title>
  ...       </head>
  ...       <body>
  ...         <div>Hello world !!!</div>
  ...       </body>
  ...     </html>'''
  ...     return resp(environ, start_response)

Now you can use the :class:`~saladedefruits.saladier.Saladier`::

  >>> from saladedefruits import Saladier
  >>> saladier = Saladier(application, salade=MySalade, theme=filename)

Let's test it a bit::

  >>> from webtest import TestApp
  >>> app = TestApp(saladier)
  >>> print app.get('/') #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
  Response: 200 OK
  Content-Type: text/html; charset=UTF-8
  <html><head><title>Hello world</title><link type="text/css" rel="stylesheet" href="http://localhost/_salade/style.css"></head><body>
    <h1>SaladeDeFruits mixing</h1>
    <div id="content"><div>Hello world !!!</div>
    </div>
  </body></html>
  
It work. We have the theme title and the application content. Also links are
resolved to get some absolute urls.

As you can see, I've put a link to a static css file prefixed by `/_salade`.
This file is serve as a static file by the
:class:`saladedefruits.saladier.Saladier` if it exist in the theme directory.
Let's create one::

  >>> filename = os.path.join(dirname, 'style.css')
  >>> open(filename, 'w').write('''
  ... body {margin:0px;}
  ... ''')

And try to serve it::

  >>> print app.get('/_salade/style.css') #doctest: +ELLIPSIS
  Response: 200 OK
  Accept-Ranges: bytes
  Content-Range: bytes 0-19/20
  Content-Type: text/css
  Etag: ...
  Last-Modified: ...
  body {margin:0px;}
  
Just work fine. Enjoy !

Of course, you can use a paste configuration instead of python stuff. You just
need to point out you theme and :class:`~saladedefruits.salade.Salade` class:

.. sourcecode:: ini

    [filter:salade]
    use = egg:SaladeDeFruits
    salade = mymodule.MySalade
    theme = %(here)s/theme/index.html

..
  >>> shutil.rmtree(dirname)

"""
