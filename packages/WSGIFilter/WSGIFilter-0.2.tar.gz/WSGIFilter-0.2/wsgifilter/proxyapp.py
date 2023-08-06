"""
WSGI proxy application that applies a deliverance theme while
passing the request to another HTTP server
"""

import urlparse
from cStringIO import StringIO
import threading
import sys
from paste.proxy import TransparentProxy
from paste.request import construct_url

class ForcedProxy(object):

    def __init__(self, remote, force_host=True, logger=None):
        self.remote = remote
        self.remote_parts = urlparse.urlsplit(remote, 'http')
        self.force_host = force_host
        if force_host:
            proxy_force_host = self.remote_parts[1]
        else:
            proxy_force_host = None
        self.logger = logger
        self.proxy_app = TransparentProxy(
            force_host=proxy_force_host)

    def __repr__(self):
        return '<%s %s remote=%r force_host=%r>' % (
            self.__class__.__name__,
            hex(id(self)),
            self.remote,
            self.force_host)

    def __call__(self, environ, start_response):
        if self.force_host:
            environ['HTTP_X_FORWARDED_SERVER'] = environ.get('HTTP_HOST', '')
            environ['HTTP_HOST'] = self.remote_parts[1]
            environ['HTTP_X_FORWARDED_SCHEME'] = environ['wsgi.url_scheme']
            environ['HTTP_X_FORWARDED_PATH'] = environ.get('SCRIPT_NAME', '')
            remote_netloc = self.remote_parts[1]
            if ':' in remote_netloc:
                remote_host, remote_port = remote_netloc.split(':', 1)
            else:
                remote_host = remote_netloc
                if environ['wsgi.url_scheme'] == 'http':
                    remote_port = '80'
                else:
                    remote_port = '443'
            environ['SERVER_NAME'] = remote_host
            environ['SERVER_PORT'] = remote_port
            environ['wsgi.url_scheme'] = self.remote_parts[0]
        remote_qs = self.remote_parts[4]
        if remote_qs:
            cur = environ.get('QUERY_STRING', '')
            if cur:
                cur += '&' + remote_qs
            else:
                cur = remote_qs
            environ['QUERY_STRING'] = remote_qs
        environ['SCRIPT_NAME'] = self.remote_parts[2]
        # leave PATH_INFO alone
        # @@: Should handle username/password
        if self.logger is not None:
            self.logger.info('Fetching remote URL %r' % construct_url(environ))
        return self.proxy_app(environ, start_response)
    

class DebugHeaders(object):

    translate_keys = {
        'CONTENT_LENGTH': 'HTTP_CONTENT_LENGTH',
        'CONTENT_TYPE': 'HTTP_CONTENT_TYPE',
        }

    def __init__(self, app, show_body=False, output=sys.stdout):
        self.app = app
        self.show_body = show_body
        self.output = output or sys.stdout

    def __call__(self, environ, start_response):
        from paste.request import construct_url
        self.output.write(
            'Incoming headers: (%s %s SCRIPT_NAME=%r)\n' %
            (environ['REQUEST_METHOD'], construct_url(environ), environ.get('SCRIPT_NAME')))
        for name, value in sorted(environ.items()):
            name = self.translate_keys.get(name, name)
            if not name.startswith('HTTP_'):
                continue
            name = name[5:].replace('_', '-').title()
            self.output.write('  %s: %s\n' % (name, value))
        if self.show_body:
            self.show_request_body(environ)
        def repl_start_response(status, headers, exc_info=None):
            self.output.write('Outgoing headers: (%s)\n' % status)
            for name, value in headers:
                self.output.write('  %s: %s\n' % (name.title(), value))
            start_response(status, headers, exc_info)
        return self.app(environ, repl_start_response)

    def show_request_body(self, environ):
        length = int(environ.get('CONTENT_LENGTH') or '0')
        body = environ['wsgi.input'].read(length)
        environ['wsgi.input'] = StringIO(body)
        if body:
            for line in body.splitlines():
                # This way we won't print out control characters:
                self.output.write(line.encode('string_escape')+'\n')
            self.output.write('-'*70+'\n')

def make_debug_headers(app, global_conf, show_body=False,
                       stderr=False):
    """
    Show all the headers that come to the application.

    These are printed to sys.stdout, or sys.stderr if stderr=True.  If
    show_body is true, then the body of all requests is also
    displayed.
    """
    from paste.deploy.converters import asbool
    if asbool(stderr):
        output = sys.stderr
    else:
        output = sys.stdout
    return DebugHeaders(app, show_body=asbool(show_body),
                        output=output)
