from myghtyutils.util import PrefixArgs
from myghtyutils.container import *

cache_config = None

try:
    from paste.registry import StackedObjectProxy
    cache_manager = StackedObjectProxy()
except:
    pass

class Cache:
    """Front-end to the containment API implementing a data cache.
    
    This is a per-request object and is not synchronized against other threads
    or processes.  (the containment API it talks to, is).
    
    """
    def __init__(self, cache_info={}, type=None, container_class=None , debug_file=None, **params):
        self.params = CacheArgs()
        self.params.set_params(**params)
        self.type = type
        self.namespace = cache_info.get('name')
        self.dict = {}
        
        self.context = cache_info.setdefault('container_context',
            ContainerContext(log_file = debug_file))
        
        if type is not None:
            self.container_class = container_registry(type, 'Container')
        elif container_class is None:
            if params.setdefault('data_dir', None) is not None:
                # DBMContainer is definitely faster than FileContainer
                # for caching
                self.container_class = DBMContainer
            else:
                self.container_class = MemoryContainer
        else:
            self.container_class = container_class
    
    def _get_container(self, key, **params):
        if not self.dict.has_key(key):
            self.dict[key] = self._create_container(self.namespace, key, **params)
        return self.dict[key]
    
    def _create_container(self, namespace, key, type=None, container_class=None, **params):
        if container_class is None:
            if type is not None:
                container_class = container_registry(type, 'Container')
            else:
                container_class = self.container_class
        cparams = self.params.get_params(**params)
        
        return container_class(context=self.context, namespace=namespace,
            key=key, **cparams)
    
    def set_container(self, key, **params):
        self.dict[key] = self._create_container(self.namespace, key, **params)
        return self.dict[key]
    
    def get_container(self, key, **params):
        return self._get_container(key, **params)
    
    def get_value(self, key, **params):
        return self._get_container(key, **params).get_value()
    
    def set_value(self, key, value, **params):
        self._get_container(key, **params).set_value(value)
    
    def remove_value(self, key):
        if self.dict.has_key(key):
            self.dict[key].clear_value()
            del self.dict[key]
    
    def clear(self):
        for key in self.dict.keys():
            self.dict[key].clear_value()
            self.dict = {}
    
    # public dict interface
    def __getitem__(self, key):
        return self.get_value(key)
    
    def __contains__(self, key): 
        container = self._get_container(key)
        return container.has_current_value()
    
    def has_key(self, key): 
        container = self._get_container(key)
        return container.has_current_value()
    
    def __delitem__(self, key):
        self.remove_value(key)
    
    def __setitem__(self, key, value):
        self.set_value(key, value)

class CacheManager(object):
    def __init__(self, **params):
        self.params = params
        self.caches = {}
    
    def get_cache(self, name, **params):
        cache_info = self.caches.setdefault(name, dict(name=name))
        cparams = self.params.copy()
        cparams.update(params)
        print cache_info
        return Cache(cache_info, **cparams)

class CacheMiddleware(object):
    def __init__(self, app, global_conf={}, **params):
        self.app = app
        cache_params = CacheArgs(**global_conf)
        cache_params.set_prefix_params(**params)
        self.cache_manager = CacheManager(**cache_params.params)
    
    def __call__(self, environ, start_response):
        if environ.get('paste.registry'):
            environ['paste.registry'].register(cache_manager, self.cache_manager)
        environ['beaker.cache'] = self.cache_manager
        return self.app(environ, start_response)

class CacheArgs(PrefixArgs):
    def __init__(self, **params):
        PrefixArgs.__init__(self, 'cache_')
        self.set_prefix_params(**params)
        
    def clone(self, **params):
        p = self.get_params(**params)
        arg = CacheArgs()
        arg.params = p
        return arg
