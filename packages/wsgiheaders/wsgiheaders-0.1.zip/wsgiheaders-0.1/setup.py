from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='wsgiheaders',
      version=version,
      description="Adding and replacing response headers",
      long_description="""\
Adding and replacing response headers
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
 >>> @addheader([('http://.*', xrds)])
 ... def app(environ, start_response):
 ...     start_response('200 OK',
 ...                    [('Content-type', 'text/plain')])
 ...     return ['Hello, world!']
 >>> app = webtest.TestApp(app)
 >>> res = app.get('/')
 >>> res.headers['X-XRDS']
 'http://localhost/svc.xrds'

""",
      classifiers=[
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha"
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
