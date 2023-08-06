from paste.fixture import TestApp
from simplejson import dumps
from cgi import parse_qsl
from trestle.json import odict


LIST = [1, 2, 3, "a cow", "a monkey", [2, 5, 6], "the end"]
DICT = odict(
    [("a", 1), ("b", "hello"), ("another", [5, 1, 9]),
     ("sub", {"key": "value"})])
STRING = "The quick brown dog jumped over the lazy fox. Again."
NUMBER = 1293039483


def app(environ, start_response):
    start_response('200 Ok', [('Content-type', 'application/json')])

    thing = environ['PATH_INFO'][1:].upper()

    if environ['REQUEST_METHOD'] == 'GET':        
        return [dumps(globals()[thing])]
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
