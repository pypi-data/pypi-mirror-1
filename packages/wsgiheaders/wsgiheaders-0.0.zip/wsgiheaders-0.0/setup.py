from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='wsgiheaders',
      version=version,
      description="Adding and replacing response headers",
      long_description="""\
Adding and replacing response headers
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

""",
      classifiers=[
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha"
        ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Atsushi Odagiri',
      author_email='aodagx@gmail.com',
      url='http://www.bitbucket.org/aodag/wsgiheaders/',
      license='MIT License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "WebOb",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
