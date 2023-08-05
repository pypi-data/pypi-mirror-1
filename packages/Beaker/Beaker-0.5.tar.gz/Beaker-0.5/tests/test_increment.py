from paste.fixture import *
from beaker.session import SessionMiddleware

def simple_app(environ, start_response):
    session = environ['beaker.session']
    if not session.has_key('value'):
        session['value'] = 0
    session['value'] += 1
    session.save()
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['The current value is: %d' % session['value']]

def test_increment():
    app = TestApp(SessionMiddleware(simple_app))
    res = app.get('/')
    assert 'current value is: 1' in res
    res = app.get('/')
    assert 'current value is: 2' in res
    res = app.get('/')
    assert 'current value is: 3' in res



if __name__ == '__main__':
    from paste import httpserver
    wsgi_app = MyghtySessionMiddleware(simple_app, {})
    httpserver.serve(wsgi_app, host='127.0.0.1', port=8080)
