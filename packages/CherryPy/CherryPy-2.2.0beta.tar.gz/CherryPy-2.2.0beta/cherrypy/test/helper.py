"""A library of helper functions for the CherryPy test suite.

The actual script that runs the entire CP test suite is called
"test.py" (in this folder); test.py calls this module as a library.

Usage:
  Each individual test_*.py module imports this module (helper),
  usually to make an instance of CPWebCase, and then call testmain().
  
  The CP test suite script (test.py) imports this module and calls
  run_test_suite, possibly more than once. CP applications may also
  import test.py (to use TestHarness), which then calls helper.py.
"""

# GREAT CARE has been taken to separate this module from test.py,
# because different consumers of each have mutually-exclusive import
# requirements. So don't go moving functions from here into test.py,
# or vice-versa, unless you *really* know what you're doing.

import os, os.path
import re
import socket
import StringIO
import sys
import thread
import threading
import time
import types

import cherrypy
from cherrypy import _cpwsgi
from cherrypy.lib import httptools
import webtest

for _x in dir(cherrypy):
    y = getattr(cherrypy, _x)
    if isinstance(y, types.ClassType) and issubclass(y, cherrypy.Error):
        webtest.ignored_exceptions.append(y)


def onerror():
    """Assign to _cp_on_error to enable webtest server-side debugging."""
    handled = webtest.server_error()
    if not handled:
        cherrypy._cputil._cp_on_error()


def error_middleware(environ, start_response):
    started = [False]
    def start(s, h, exc=None):
        started[0] = True
        start_response(s, h, exc)
    
    try:
        for chunk in _cpwsgi.wsgiApp(environ, start):
            yield chunk
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception, x:
        # We should only reach this point if server.throw_errors is True.
        if not started[0]:
            start_response("500 Server Error", [])
        yield "THROWN ERROR: %s" % x.__class__.__name__


class TestWSGI(_cpwsgi.WSGIServer):
    """Wrapper for WSGI server so we can test thrown errors."""
    
    def __init__(self):
        _cpwsgi.WSGIServer.__init__(self, error_middleware)


class CPWebCase(webtest.WebCase):
    
    mount_point = ""
    
    def prefix(self):
        return self.mount_point.rstrip("/")
    
    def exit(self):
        sys.exit()
    
    def _getRequest(self, url, headers, method, body):
        # Like getPage, but for serverless requests.
        webtest.ServerError.on = False
        self.url = url
        
        requestLine = "%s %s HTTP/1.1" % (method.upper(), url)
        headers = webtest.cleanHeaders(headers, method, body,
                                       self.HOST, self.PORT)
        if body is not None:
            body = StringIO.StringIO(body)
        
        request = cherrypy.server.request((self.HOST, self.PORT), self.HOST, "http")
        response = request.run(requestLine, headers, body)
        
        self.status = response.status
        self.headers = response.header_list
        
        # Build a list of request cookies from the previous response cookies.
        self.cookies = [('Cookie', v) for k, v in self.headers
                        if k.lower() == 'set-cookie']
        
        try:
            self.body = []
            for chunk in response.body:
                self.body.append(chunk)
            request.close()
        except Exception, ex:
            if cherrypy.config.get("stream_response", False):
                try:
                    request.close()
                except:
                    cherrypy.log(cherrypy._cputil.formatExc())
                # Pass the error through
                raise ex
            
            s, h, b = cherrypy._cputil.bareError()
            # Don't reset status or headers; we're emulating an error which
            # occurs after status and headers have been written to the client.
            for chunk in b:
                self.body.append(chunk)
        self.body = "".join(self.body)
        
        if webtest.ServerError.on:
            self.tearDown()
            raise webtest.ServerError()
    
    def tearDown(self):
        pass
    
    def getPage(self, url, headers=None, method="GET", body=None):
        """Open the url with debugging support. Return status, headers, body."""
        # Install a custom error handler, so errors in the server will:
        # 1) show server tracebacks in the test output, and
        # 2) stop the HTTP request (if any) and ignore further assertions.
        cherrypy.root._cp_on_error = onerror
        # Backward compatibility:
        cherrypy.root._cpOnError = onerror
        
        if self.mount_point:
            url = httptools.urljoin(self.mount_point, url)
        
        if cherrypy.server.httpserver is None:
            self._getRequest(url, headers, method, body)
        else:
            webtest.WebCase.getPage(self, url, headers, method, body)
    
    def assertErrorPage(self, status, message=None, pattern=''):
        """ Compare the response body with a built in error page.
            The function will optionally look for the regexp pattern, 
            within the exception embedded in the error page.
        """
        
        # This will never contain a traceback:
        page = cherrypy._cputil.getErrorPage(status, message=message)
        
        # First, test the response body without checking the traceback.
        # Stick a match-all group (.*) in to grab the traceback.
        esc = re.escape
        epage = esc(page)
        epage = epage.replace(esc('<pre id="traceback"></pre>'),
                              esc('<pre id="traceback">')
                              + '(.*)' + esc('</pre>'))
        m = re.match(epage, self.body, re.DOTALL)
        if not m:
            self._handlewebError('Error page does not match\n' + page)
            return
        
        # Now test the pattern against the traceback
        if pattern is None:
            # Special-case None to mean that there should be *no* traceback.
            if m and m.group(1):
                self._handlewebError('Error page contains traceback')
        else:
            if (m is None) or (not re.search(re.escape(pattern), m.group(1))):
                msg = 'Error page does not contain %s in traceback'
                self._handlewebError(msg % repr(pattern))


CPTestLoader = webtest.ReloadingTestLoader()
CPTestRunner = webtest.TerseTestRunner(verbosity=2)

def setConfig(conf):
    """Set the config using a copy of conf."""
    if isinstance(conf, basestring):
        # assume it's a filename
        cherrypy.config.update(file=conf)
    else:
        cherrypy.config.update(conf.copy())


def run_test_suite(moduleNames, server, conf):
    """Run the given test modules using the given server and conf.
    
    The server is started and stopped once, regardless of the number
    of test modules. The config, however, is reset for each module.
    """
    setConfig(conf)
    cherrypy.server.start_with_callback(_run_test_suite_thread,
            args = (moduleNames, conf), server_class = server)

def _run_test_suite_thread(moduleNames, conf):
    for testmod in moduleNames:
        # Must run each module in a separate suite,
        # because each module uses/overwrites cherrypy globals.
        cherrypy.root = None
        cherrypy.config.reset()
        setConfig(conf)
        
        suite = CPTestLoader.loadTestsFromName(testmod)
        CPTestRunner.run(suite)
    thread.interrupt_main()

def testmain(server=None, conf=None):
    """Run __main__ as a test module, with webtest debugging."""
    if conf is None:
        conf = {}
    setConfig(conf)
    cherrypy.server.start_with_callback(_test_main_thread,
            server_class = server)

def _test_main_thread():
    try:
        webtest.WebCase.PORT = cherrypy.config.get('server.socket_port')
        webtest.main()
    finally:
        thread.interrupt_main()

