#!/usr/bin/env python2.4
"""yaro - Yet Another Request Object (for WSGI)

A simple but non-restrictive abstraction of WSGI for end users.

(See the docstrings of the various functions and classes.)

Copyright (C) 2006 Luke Arno - http://lukearno.com/

This program is free software; you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by the 
Free Software Foundation; either version 2 of the License, or (at your 
option) any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.

Luke Arno can be found at http://lukearno.com/

"""

import urllib
import cgi
import mimetypes

from wsgiref import headers, util


class URI(object):
    """URI info from a WSGI environ."""

    def __init__(self, environ):
        """Just pass in environ to populate."""
        self.scheme = environ['wsgi.url_scheme']
        if environ.get('HTTP_HOST'):
            self.host = environ['HTTP_HOST']
            if ':' in self.host:
                self.host, self.port = self.host.split(':')
            else:
                if self.scheme == 'http':
                    self.port = '80'
                else:
                    self.port = '443'
        else:
            self.host += environ['SERVER_NAME']
            self.port += environ['SERVER_POST']
        self.script = environ.get('SCRIPT_NAME', '')
        self.path = environ.get('PATH_INFO', '')
        self.query = environ.get('QUERY_STRING')

    def __call__(self, path=None, with_qs=False):
        """Complete URI string with optional query string and path.
        
        path=None and will default to self.path (from PATH_INFO)
        with_qs=False and requests inclusion or not of query string.

        This is handy for doing redirects within your application.
        """
        if path is None:
            path = self.path
        app_uri = self.application_uri()
        if path[0] != '/':
            app_uri = '/'.join((app_uri + self.path).split('/')[:-1])
            while path[:3] == '../':
                app_uri = '/'.join(app_uri.split('/')[:-1])
                path = path[3:]
            path = '/' + path
        uri = app_uri + urllib.quote(path)
        if with_qs and self.query:
            uri += '?' + self.query
        return uri

    def server_uri(self):
        """URI of server with no script_name or path_info or query_string."""
        uri = self.scheme + '://' + self.host
        if self.scheme + self.port not in ('http80', 'https443'):
            uri += ':' + self.port
        return uri

    def application_uri(self):
        """URI up to and including script_name."""
        return self.server_uri() + urllib.quote(self.script)


class Request(object):
    """Yet another request object (for WSGI), as advertised."""

    def __init__(self, environ):
        """Set up the various attributes."""
        self.environ = environ
        self.method = environ['REQUEST_METHOD']
        self.content_type = environ.get('CONTENT_TYPE', '')
        self.content_length = environ.get('CONTENT_LENGTH', '')
        self.uri = URI(environ)
        self.res = Response(self.uri())
        self._parse_query()
        self._parse_form()

    def _parse_query(self):
        """Populate a dictionary in self.query from the querystring.
        
        The dictionary created will have strings or lists of strings
        as its values.
        
        If you have a parameter like ?foo[]=bar then 
        self.query['foo'] == ['bar'] ('bar' will be in a list even if 
        it has only one member). The key will be 'foo'.

        In other words, this is a way to indicate that you want a 
        list and avoid boilerplate.

        When a name does not end in brackets, you will end up with a 
        list only if there is more than one parameter by that name.

        If 'foo[]' and 'foo' are both used as input names, they will 
        step on each other. Use one or the other.
        """
        qu = cgi.parse_qs(self.uri.query)
        query = {}
        for key, value in qu.iteritems():
            if key.endswith('[]'):
                if not isinstance(value, list):
                    value = [value]
                query[key[:-2]] = value
            else:
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                query[key] = value
        self.query = query

    def _parse_form(self):
        """Populate a dictionary in self.form from webform data.
        
        The dictionary created will have strings, cgi.FieldStorage 
        objects (used for file uploads) or lists of strings and/or 
        cgi.FieldStorage objects as its values.
        
        If your form data has an field named "foo[]", its value 
        will be found in self.form in a list even if it has only 
        one member. The key will be 'foo'.

        In other words, this is a way to indicate that you want a
        list and avoid boilerplate.

        When a name does not end in brackets, you will end up with 
        a list only if there is more than one field by that name.

        If 'foo[]' and 'foo' are both used as input names, they 
        will step on each other. Use one or the other.
        """
        fs = cgi.FieldStorage(fp=self.environ['wsgi.input'],
                              environ=self.environ,
                              keep_blank_values=True) 
        form = {}
        for key in fs:
            value = fs[key]
            if key.endswith("[]"):
                if not isinstance(value, list):
                    value = [value]
                key = key[:-2]
            if isinstance(value, list):
                newvalue = []
                for v in value:
                    if v.filename:
                        newvalue.append(v)
                    else:
                        newvalue.append(v.value)
                form[key] = newvalue
            else:
                if value.filename is None:
                    value = value.value
                form[key] = value
        self.form = form

    def redirect(self, location, permanent=True):
        """Set the location header and status."""
        self.res.headers['Location'] = location
        if permanent is True:
            self.res.status = "301 Moved Permanently" 
        else:
            self.res.status = "302 Found"


class Response(object):
    """Hold on to info about the response to a request."""

    def __init__(self, uri):
        """Set up various useful defaults."""
        self._headers = []
        self.headers = headers.Headers(self._headers)
        guess = mimetypes.guess_type(uri)[0]
        self.headers['Content-Type'] = guess or 'text/plain'
        self.status = '200 OK'
        self.body = ""


class Yaro(object):
    """WSGI wrapper for something that takes and returns Request."""

    def __init__(self, app):
        """Take the thing to wrap."""
        self.app = app
        
    def __call__(self, environ, start_response):
        """Create Request, call thing, unwrap results and respond."""
        environ['yaro.request'] = req = Request(environ)
        body = self.app(req)
        if body is None:
            body = req.res.body
        start_response(req.res.status, req.res._headers)
        if isinstance(body, str):
            return [body]
        elif isiterable(body):
            return body
        else:
            return util.FileWrapper(body)


def isiterable(it):
    """Return True if 'it' is iterable else return False."""
    try:
        iter(it)
    except:
        return False
    else:
        return True


if __name__ == '__main__':

    import code
    
    from wsgiref.simple_server import make_server

    def foo(req):
        #req.res.body = 'Hello, World!'
        code.interact(local=locals(), banner="%s: %s" % (req.method, req.uri()))
        if not req.uri.path.endswith('.txt'):
            req.redirect('../proudhon.txt')
        else:
            req.res.body = req.uri()

    try:
        make_server('localhost', 9999, Yaro(foo)).serve_forever()
    except KeyboardInterrupt, ki:
        print 'I said "Good day!"'
