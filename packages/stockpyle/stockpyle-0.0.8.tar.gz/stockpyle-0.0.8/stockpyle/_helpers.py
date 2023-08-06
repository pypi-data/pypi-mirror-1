class KeyValueHelper(object):
    """Internal helper object that can generate unique keys for a store that
    stores objects in key/value pairs.  Given a class/instance and a property
    dictionary, this helper creates a unique lookup key (e.g. 'mymodule.MyClass(foo=abc;bar=123)')"""
    
    def __init__(self, polymorphic=False, prefix="stockpyle"):
        self.__stockpyle_bases_lookup = {}
        self.__polymorphic = polymorphic
        self.__prefix = prefix
    
    def generate_verbose_lookup_key(self, target_klass, properties):
        properties_str = self.__create_properties_str(properties)
        return "%s:%s.%s(%s)" % (self.__prefix, str(target_klass.__module__), target_klass.__name__, properties_str)

    def generate_terse_lookup_key(self, target_klass, properties):
        properties_str = self.__create_properties_str(properties)
        return "%s:%s.%s(%s)" % (self.__prefix, str(target_klass.__module__), target_klass.__name__, hash(properties_str))
    
    def generate_all_verbose_lookup_keys(self, obj):
        return self.__generate_all_lookup_keys(obj, self.generate_verbose_lookup_key)
        
    def generate_all_terse_lookup_keys(self, obj):
        return self.__generate_all_lookup_keys(obj, self.generate_terse_lookup_key)
    
    def __create_properties_str(self, properties):
        return ";".join(sorted(["%s=%s" % kv for kv in properties.iteritems()]))
    
    def __generate_all_lookup_keys(self, obj, generate_lookup_key_callback):
        lookup_keys = []
        klasses = [obj.__class__]
        if self.__polymorphic:
            klasses += self.__get_stockpyle_base_classes(obj.__class__)
        for klass in klasses:
            for stockpyle_key in klass.__stockpyle_keys__:
                if isinstance(stockpyle_key, tuple):
                    property_names = stockpyle_key
                else:
                    property_names = tuple([stockpyle_key])
                property_dict = self.__get_property_dict(obj, property_names)
                lookup_keys.append(generate_lookup_key_callback(klass, property_dict))
        return lookup_keys
    
    def __get_stockpyle_base_classes(self, klass):
        """returns an ordered list of stockpyle-managed base classes by recursing
        up the inheritance tree of the given class and collecting any base classes
        that have __stockpyle_keys__ defined"""
        if klass not in self.__stockpyle_bases_lookup:
            
            # we haven't calculated the stockpyle bases for this class yet
            # calculate them
            bases = []
            def collect(current_klass):
                for b in current_klass.__bases__:
                    if hasattr(b, "__stockpyle_keys__"):
                        bases.append(b)
                    collect(b)
            collect(klass)
            
            # and then save for for faster lookup later
            self.__stockpyle_bases_lookup[klass] = bases
            
        # return those bases
        return self.__stockpyle_bases_lookup[klass]
    
    def __get_property_dict(self, obj, property_names):
        """for a given object, returns a dictionary of all attributes
        with the given names"""
        properties = {}
        for n in property_names:
            properties[n] = getattr(obj, n)
        return properties
