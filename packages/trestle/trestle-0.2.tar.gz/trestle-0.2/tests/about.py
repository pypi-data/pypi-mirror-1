from paste.fixture import TestApp
from cgi import parse_qsl

def app(environ, start_response):
    start_response('200 Ok', [('Content-type', 'text/plain')])

    if environ['REQUEST_METHOD'] == 'GET':
        return ['Hello']
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


class SpecialTestApp(TestApp):
    special = False

    def get(self, url, *arg, **kw):
        if url == '/special':
            if self.special:
                r = "SPECIAL is set."
            else:
                r = "SPECIAL is not set."
            res = self._make_response(('200 OK', [], r, []), 0)
            return res
        return super(SpecialTestApp, self).get(url, *arg, **kw)
        
    def setup_special(self):
        self.special = True

    def teardown_special(self):
        self.special = False


client = SpecialTestApp(app)
