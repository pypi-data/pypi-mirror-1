#
"""

Copyright (c) 2009 Atsushi Odagiri

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

>>> import re
>>> p = re.compile(r'.*\.html')
>>> @replaceheader([(p, [('Content-type', 'text/html')])])
... def app(environ, start_response):
...     start_response('200 OK',
...                    [('Content-type', 'text/plain')])
...     return ['Hello, world!']
>>> import webtest
>>> app = webtest.TestApp(app)
>>> res = app.get('/a.txt')
>>> res.content_type
'text/plain'
>>> res = app.get('/a.html')
>>> res.content_type
'text/html'
>>> p = re.compile(r'.*')
>>> @addheader([(p, [('X-XRDS', 'http://localhost/services.xrds')])])
... def app(environ, start_response):
...     start_response('200 OK',
...                    [('Content-type', 'text/plain')])
...     return ['Hello, world!']
>>> app = webtest.TestApp(app)
>>> res = app.get('/')
>>> res.headers['X-XRDS']
'http://localhost/services.xrds'
"""

from webob import Request, Response

def addheader(headerConditions):
    def decorator(app):
        def wrap(environ, start_response):
            req = Request(environ)
            res = req.get_response(app)
            for pred, headers in headerConditions:
                if pred.match(req.url):
                    for name, value in headers:
                        res.headers.add(name, value)
            return res(environ, start_response)
        return wrap
    return decorator

def replaceheader(headerConditions):
    def decorator(app):
        def wrap(environ, start_response):
            req = Request(environ)
            res = req.get_response(app)
            for pred, headers in headerConditions:
                if pred.match(req.url):
                    for name, value in headers:
                        res.headers[name] = value
            return res(environ, start_response)
        return wrap
    return decorator
