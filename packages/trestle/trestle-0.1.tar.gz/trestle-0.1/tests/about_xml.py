from paste.fixture import TestApp
from cgi import parse_qsl

def app(environ, start_response):
    if environ['REQUEST_METHOD'] == 'GET':
        if 'html' in environ['PATH_INFO']:
            start_response('200 Ok', [('Content-type', 'text/html')])
            return [' <html><p>Even fairly broken html is supported</p></html>']
        else:
            start_response('200 Ok', [('Content-type', 'text/xml')])
            return ['<hello>This is some xml <a val="1"  />.</hello>']
    elif environ['REQUEST_METHOD'] == 'POST':
        start_response('200 Ok', [('Content-type', 'text/xml')])
        post_data = str(environ['wsgi.input'].read())
        params = parse_qsl(post_data)
        return ['You said: ', 
                ' and '.join('%s=%s' % p for p in params)]

def setup_all(cls):
    pass

def teardown_all(cls):
    pass

def setup_each(inst):
    pass

def teardown_each(inst):
    pass


client = TestApp(app)
