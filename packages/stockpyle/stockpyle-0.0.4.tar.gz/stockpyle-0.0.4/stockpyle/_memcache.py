import time
from datetime import datetime, timedelta
from stockpyle._base import BaseStore


class MemcacheStore(BaseStore):
    
    def __init__(self, client=None, servers=None):
        
        super(MemcacheStore, self).__init__()
        
        if client and servers:
            raise ValueError("cannot give both a client and a list of servers, only one is allowed")
            
        if client:
            self.__client = client
        elif servers:
            import memcache
            self.__client = memcache.Client(servers)
        else:
            raise ValueError("you must specify either a client or a list of servers for memcache")
    
    def _get_lifetime(self, obj):

        # get default lifetime
        lifetime = super(MemcacheStore, self)._get_lifetime(obj)
        
        # ensure that lifetime is in unixtime or seconds
        if isinstance(lifetime, datetime):
            lifetime = time.mktime(lifetime.timetuple())
        elif isinstance(lifetime, timedelta):
            lifetime = 86400*lifetime.days + lifetime.seconds + lifetime.microseconds/1000000.0
        
        return lifetime
    
    def put(self, obj):
        lifetime = self._get_lifetime(obj)
        object_map = {}
        for k in self._generate_all_terse_lookup_keys(obj):
            object_map[k] = obj
        self.__client.set_multi(object_map, lifetime)
        
    def batch_put(self, objs):
        
        # group puts by lifetime
        lifetime_lookup = {}
        for obj in objs:
            lifetime = self._get_lifetime(obj)
            if lifetime not in lifetime_lookup:
                lifetime_lookup[lifetime] = []
            lifetime_lookup[lifetime].append(obj)
        
        for lifetime in lifetime_lookup:
            objs_with_same_lifetime = lifetime_lookup[lifetime]
            object_map = {}
            for obj in objs_with_same_lifetime:
                for k in self._generate_all_terse_lookup_keys(obj):
                    object_map[k] = obj
            self.__client.set_multi(object_map, lifetime)
    
    def delete(self, obj):
        cachekeys = self._generate_all_terse_lookup_keys(obj)
        self.__client.delete_multi(cachekeys)
    
    def get(self, klass, key):
        cachekey = self._generate_terse_lookup_key(klass, key)
        return self.__client.get(cachekey)
    
    def batch_get(self, klass, keys):
        cachekeys = [self._generate_terse_lookup_key(klass, properties) for properties in keys]
        object_map = self.__client.get_multi(cachekeys)
        return [object_map.get(k, None) for k in cachekeys]
    