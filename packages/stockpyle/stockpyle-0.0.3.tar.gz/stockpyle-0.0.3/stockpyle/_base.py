class BaseStore(object):
    """represents a standard storage container"""
    
    def _generate_verbose_lookup_key(self, target_klass, properties):
        properties_str = ";".join(["%s=%s" for k,v in properties.iteritems()])
        return "%s.%s(%s)" % (str(target_klass.__module__), target_klass.__name__, properties_str)

    def _generate_terse_lookup_key(self, target_klass, properties):
        properties_str = ";".join(["%s=%s" for k,v in properties.iteritems()])
        return "%s.%s(%s)" % (str(target_klass.__module__), target_klass.__name__, hash(properties_str))
    
    def _generate_all_verbose_lookup_keys(self, obj):
        return self.__generate_all_lookup_keys(obj, self._generate_verbose_lookup_key)
        
    def _generate_all_terse_lookup_keys(self, obj):
        return self.__generate_all_lookup_keys(obj, self._generate_terse_lookup_key)
    
    def __get_property_dict(self, obj, property_names):
        properties = {}
        for n in property_names:
            properties[n] = getattr(obj, n)
        return properties
    
    def __generate_all_lookup_keys(self, obj, generate_lookup_key_callback):
        lookup_keys = []
        for stockpyle_key in obj.__stockpyle_keys__:
            if isinstance(stockpyle_key, tuple):
                property_names = stockpyle_key
            else:
                property_names = tuple([stockpyle_key])
            property_dict = self.__get_property_dict(obj, property_names)
            lookup_keys.append(generate_lookup_key_callback(obj.__class__, property_dict))
        return lookup_keys
    
    def __init__(self):
        self.__lifetime_lookup = {}
    
    def _get_lifetime(self, obj):
        return self.__lifetime_lookup.get(obj.__class__, None)
    
    def configure(self, classes, lifetime):
        for c in classes:
            self.__lifetime_lookup[c] = lifetime
        
    def put(self, obj):
        raise NotImplementedError()
        
    def batch_put(self, objs):
        raise NotImplementedError()
    
    def delete(self, obj):
        raise NotImplementedError()
    
    def get(self, klass, key):
        raise NotImplementedError()
    
    def batch_get(self, klass, keys):
        raise NotImplementedError()
    
