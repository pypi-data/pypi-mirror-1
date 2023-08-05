from paste.fixture import *
from beaker.cache import CacheMiddleware

def simple_app(environ, start_response):
    cache = environ['beaker.cache'].get_cache('testcache')
    try:
        value = cache.get_value('value')
    except:
        value = 0
    cache.set_value('value', value+1)
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['The current value is: %s' % cache.get_value('value')]

def test_increment():
    app = TestApp(CacheMiddleware(simple_app))
    res = app.get('/')
    assert 'current value is: 1' in res
    res = app.get('/')
    assert 'current value is: 2' in res
    res = app.get('/')
    assert 'current value is: 3' in res
