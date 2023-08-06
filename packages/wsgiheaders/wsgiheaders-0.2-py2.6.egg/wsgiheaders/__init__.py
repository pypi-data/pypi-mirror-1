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

>>> @replaceheader([(r'.*\.html', [('Content-type', 'text/html')])])
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
>>> def xrds(environ):
...     return [('X-XRDS', environ['wsgi.url_scheme'] + '://' + environ['SERVER_NAME'] + '/svc.xrds')]
... 
>>> def predicate(environ):
...     return environ.get('HTTP_ACCEPT', '').find('application/xrds+xml') != -1
... 
>>> @addheader([(predicate, xrds)])
... def app(environ, start_response):
...     start_response('200 OK',
...                    [('Content-type', 'text/plain')])
...     return ['Hello, world!']
>>> app = webtest.TestApp(app)
>>> res = app.get('/')
>>> 'X-XRDS' in res.headers
False
>>> res = app.get('/', headers={'Accept':'application/xrds+xml'})
>>> res.headers['X-XRDS']
'http://localhost/svc.xrds'
"""

import re
from webob import Request, Response

def addheaderhandler(res, name, value):
    res.headers.add(name, value)

def addheader(headerConditions):
    return wsgiheader(headerConditions, addheaderhandler)

def replaceheaderhandler(res, name, value):
    res.headers[name] = value

def replaceheader(headerConditions):
    return wsgiheader(headerConditions, replaceheaderhandler)

def wsgiheader(headerConditions, handler):
    headerConditions = [(re.compile(p) if isinstance(p, basestring) else p,
                         headers)
                        for p,headers in headerConditions ]
    def decorator(app):
        def wrap(environ, start_response):
            req = Request(environ)
            res = req.get_response(app)
            for pred, headers in headerConditions:
                if callable(pred):
		    flg = pred(environ)
                else:
                    flg = pred.match(req.url)

                if flg:
                    if callable(headers):
                        headers = headers(environ)
                    for name, value in headers:
                        handler(res, name, value)
            return res(environ, start_response)
        return wrap
    return decorator
