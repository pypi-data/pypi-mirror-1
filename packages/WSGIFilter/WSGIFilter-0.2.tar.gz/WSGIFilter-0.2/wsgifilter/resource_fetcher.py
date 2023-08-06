from StringIO import StringIO
from paste.wsgilib import intercept_output
from paste.proxy import TransparentProxy 
from paste.request import construct_url
from paste.response import header_value
import urlparse
import urllib
import webob


__all__ = ['get_internal_resource', 'get_external_resource']

#next two classes are based on code from deliverance
class Response(webob.Response):
    default_charset = None
    unicode_errors = 'replace'

    def _unicode_body__get(self):
        """
        Get/set the unicode value of the body (using the charset of the Content-Type)
        """
        if not self.charset:
            return self.body
        body = self.body
        return body.decode(self.charset, self.unicode_errors)

    def _unicode_body__del(self):
        del self.body

    unicode_body = property(_unicode_body__get, None, _unicode_body__del, doc=_unicode_body__get.__doc__)

class Request(webob.Request):
    ResponseClass = Response


def prep_environ(uri, in_environ=None, headers_only = False):
    uri = urllib.unquote(uri)
    loc = urlparse.urlsplit(uri) 

    if in_environ:
        environ = in_environ.copy()
    else:
        environ = {}

    if 'HTTP_ACCEPT_ENCODING' in environ:
        environ['HTTP_ACCEPT_ENCODING'] = '' 

    if headers_only: 
        environ['REQUEST_METHOD'] = 'HEAD'
    else:
        environ['REQUEST_METHOD'] = 'GET'

    environ['CONTENT_LENGTH'] = '0'
    environ['wsgi.input'] = StringIO('')

    environ['wsgi.url_scheme'] = loc[0]
    environ['wsgi.version'] = (1, 0)
    environ['HTTP_HOST'] = loc[1]
    environ['PATH_INFO'] = loc[2]
    environ['QUERY_STRING'] = loc[3]
    environ['SCRIPT_NAME'] = ''
    ## FIXME: this should probably only include known-good keys,
    ## not exclude known-bad keys
    for key in ['CONTENT_TYPE', 'paste.registry', 'paste.evalexception']:
        if key in environ:
            del environ[key]

    return environ

def get_internal_resource(uri, in_environ, app, headers_only=False,
                          add_to_environ=None):
    if 'paste.recursive.include' in in_environ:
        includer = in_environ['paste.recursive.include']
        environ = prep_environ(uri, in_environ=includer.original_environ,
                               headers_only=headers_only)
        if add_to_environ:
            environ = environ.copy()
            environ.update(add_to_environ)
        environ['paste.recursive.include'] = in_environ['paste.recursive.include']
        app = includer.application
    else: 
        environ = prep_environ(uri, in_environ=in_environ,
                               headers_only=headers_only)
        if add_to_environ:
            environ = environ.copy()
            environ.update(add_to_environ)

    req = Request(environ)
    res = req.get_response(app)

    status, headers, body = res.status, res.headerlist, res.unicode_body
    return status, headers, body


def get_file_resource(uri, in_environ=None, headers_only=False):
    environ = prep_environ(uri, in_environ=in_environ,
                           headers_only=headers_only)
    path = urlparse.urlparse(uri)[2]
    file_app = FileApp(path)
    return intercept_output(environ, file_app)

def get_external_resource(uri, in_environ = None, headers_only=False): 
    environ = prep_environ(uri, in_environ=in_environ,
                           headers_only=headers_only)
    proxy_app = TransparentProxy()
    return intercept_output(environ, proxy_app)
