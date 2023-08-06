import re
from wsgifilter import *
from paste.fixture import TestApp

class UpperFilter(Filter):

    def filter(self, environ, headers, data):
        return data.upper()

class Rot13Filter(Filter):

    decode_unicode = True

    def filter(self, environ, headers, data):
        return re.sub(
            r'>[^<]*<', self.sub_section, data)

    def sub_section(self, match):
        return '>%s<' % match.group(0)[1:-1].encode('rot13')

def simple_app(environ, start_response):
    if environ.get('PATH_INFO') == '/image':
        start_response('200 OK', [('content-type', 'image/gif')])
        return ['not real image']
    start_response('200 OK', [('content-type', 'text/html')])
    return ['<html><body>This is a test</body></html>']

def wrapit(filter):
    wsgi_app = filter(simple_app)
    app = TestApp(wsgi_app)
    return app

def test_upper():
    app = wrapit(UpperFilter)
    res = app.get('/')
    assert res.body == '<HTML><BODY>THIS IS A TEST</BODY></HTML>'

def test_rot13():
    app = wrapit(Rot13Filter)
    res = app.get('/')
    assert res.body == '<html><body>Guvf vf n grfg</body></html>'

def test_mimetype():
    app = wrapit(UpperFilter)
    res = app.get('/image')
    assert res.body == 'not real image'
    
