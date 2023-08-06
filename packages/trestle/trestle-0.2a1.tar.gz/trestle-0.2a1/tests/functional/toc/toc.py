from paste.fixture import TestApp
from cgi import parse_qsl

def app(environ, start_response):
    start_response('200 Ok', [('Content-type', 'text/plain')])

    if environ['REQUEST_METHOD'] == 'GET':
        return ['ok']
    elif environ['REQUEST_METHOD'] == 'POST':
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
