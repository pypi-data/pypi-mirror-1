try:
    from paste.registry import StackedObjectProxy
    beaker_session = StackedObjectProxy()
except:
    pass
from myghtyutils.session import Session


class request(object):
    class headers_out(object):
        def __init__(self):
            self.headers = {}
        def add(self, name, value):
            self.headers[name] = value
    headers_out = headers_out()

class SessionObject(object):
    """Session proxy/lazy creator
    
    This object proxies access to the actual session object, so that in the
    case that the session hasn't been used before, it will be setup. This
    avoid creating and loading the session from persistent storage unless
    its actually used during the request.
    
    """
    def __init__(self, environ, **params):
        self.__dict__['_params'] = params
        self.__dict__['_environ'] = environ
        self.__dict__['_sessinit'] = False
        self.__dict__['_sess'] = None
        self.__dict__['_headers'] = []
    
    def _session(self):
        """Lazy initial creation of session object"""
        if not self.__dict__['_sessinit']:
            params = self.__dict__['_params']
            environ = self.__dict__['_environ']
            req = request()
            self.__dict__['_headers'] = req.headers_out
            req.headers_in = dict(cookie=environ.get('HTTP_COOKIE'))
            self.__dict__['_sess'] = Session(req, use_cookies=True, **params)
            self.__dict__['_sessinit'] = True
        return self.__dict__['_sess']
    
    def __getattr__(self, attr):
        return getattr(self._session(), attr)
    
    def __setattr__(self, attr, value):
        setattr(self._session(), name, value)
    
    def __delattr__(self, name):
        self._session().__delattr__(name)
    
    def __getitem__(self, key):
        return self._session()[key]
    
    def __setitem__(self, key, value):
        self._session()[key] = value
    
    def __delitem__(self, key):
        self._session().__delitem__(key)
    
    def __repr__(self):
        return self._session().__repr__()
    
    def __iter__(self):
        """Only works for proxying to a dict"""
        return iter(self._session().keys())
    
    def __contains__(self, key):
        return self._session().has_key(key)
    

session_params = dict(invalidate_corrupt = False, type = None, data_dir = None,
    key = 'beaker_session_id', timeout = None, secret = None, log_file = None)

class SessionMiddleware(object):
    def __init__(self, wrap_app, global_conf={}, auto_register=True, **params):
        instance_params = session_params.copy()
        for key in global_conf:
            if key.startswith('session_'):
                if key[8:] in instance_params:
                    instance_params[key[8:]] = global_conf[key]
        
        instance_params.update(params)
        self.auto_register = auto_register
        self.params = instance_params
        self.key = self.params['key']
        self.wrap_app = wrap_app
    
    def __call__(self, environ, start_response):
        session = SessionObject(environ, **self.params)
        if environ.get('paste.registry') and self.auto_register:
            environ['paste.registry'].register(beaker_session, session)
        environ['beaker.session'] = session
        
        def session_start_response(status, headers, exc_info = None):
            if session.__dict__['_sessinit']:
                cookie = session.__dict__['_headers'].headers.get('set-cookie')
                if cookie:
                    headers.append(('Set-cookie', cookie))
            return start_response(status, headers, exc_info)
        return self.wrap_app(environ, session_start_response)

def session_filter_factory(global_conf, **kwargs):
    def filter(app):
        return SessionMiddleware(app, global_conf, **kwargs)
    return filter

def session_filter_app_factory(app, global_conf, **kwargs):
    return SessionMiddleware(app, global_conf, **kwargs)
