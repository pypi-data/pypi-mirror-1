import os
import sys
from paste.urlparser import StaticURLParser

from wsgiutils.resource_fetcher import * 

def make_environ():

    environ = {
        'wsgi.url_scheme' : 'http',
        'SERVER_NAME' : 'localhost',
        'SERVER_PORT' : '80',
        'wsgi.version' : (1,0),
        }
    return environ


def make_static_url_parser(): 
    return StaticURLParser(os.path.join(os.path.dirname(__file__), 'test-data'))

def test_internal(): 
    static_app = make_static_url_parser()
    uri = "/foo.html"
    
    environ = make_environ()
    (status, headers, body) = get_internal_resource(uri, environ, static_app)
    
    if not status.startswith('200'): 
        raise ValueError(status)

def test_internal_absolute():
    static_app = make_static_url_parser()
    uri = "http://localhost/foo.html"
    
    environ = make_environ()

    (status, headers, body) = get_internal_resource(uri, environ, static_app)
    
    if not status.startswith('200'): 
        raise ValueError(status)

def test_external(): 
    (status, headers, body) = get_external_resource('http://www.google.com/')
    if not status.startswith('200'): 
        raise ValueError(status)


if __name__ == '__main__':
    pass
