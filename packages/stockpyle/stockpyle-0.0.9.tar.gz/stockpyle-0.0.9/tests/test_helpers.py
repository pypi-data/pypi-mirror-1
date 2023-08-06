from unittest import TestCase
from stockpyle._helpers import KeyValueHelper


class DummyObject(object):
    
    __stockpyle_keys__ = [("foo", "bar")]
    foo = 1
    bar = 2


class DummyObjectSubclass(DummyObject):
    
    __stockpyle_keys__ = ["zap"]
    zap = "xyz"


class DummyObjectSubSubclassWithoutStockpyleKeys(DummyObjectSubclass):
    pass


class DummyObjectSubSubSubclass(DummyObjectSubSubclassWithoutStockpyleKeys):
    
    __stockpyle_keys__ = [("foo", "blarg")]
    blarg = "abc"


class KeyValueHelperTestCase(TestCase):
    
    def setUp(self):
        self.__module_name_for_dummy_objects = str(DummyObject.__module__)
    
    def test_generates_proper_verbose_keys(self):
        
        kvh = KeyValueHelper()
        key = kvh.generate_verbose_lookup_key(DummyObject, {"xyz": "foo", "abc": 123})
        self.assertEqual(key, "stockpyle:%s.DummyObject(abc=123;xyz=foo)" % self.__module_name_for_dummy_objects)
    
    def test_generates_proper_terse_keys(self):
        
        kvh = KeyValueHelper()
        key = kvh.generate_terse_lookup_key(DummyObject, {"xyz": "foo", "abc": 123})
        self.assertEqual(key, "stockpyle:%s.DummyObject(%s)" % (self.__module_name_for_dummy_objects, hash("abc=123;xyz=foo")))
    
    def test_generates_proper_verbose_keys_list_when_nonpolymorphic(self):
        
        kvh = KeyValueHelper()
        
        # test dummy object
        keys = kvh.generate_all_verbose_lookup_keys(DummyObject())
        expected_set = set([
            "stockpyle:%s.DummyObject(%s)" % (self.__module_name_for_dummy_objects, "bar=2;foo=1")
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_verbose_lookup_keys(DummyObjectSubclass())
        expected_set = set([
            "stockpyle:%s.DummyObjectSubclass(%s)" % (self.__module_name_for_dummy_objects, "zap=xyz")
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_verbose_lookup_keys(DummyObjectSubSubclassWithoutStockpyleKeys())
        expected_set = set([
            "stockpyle:%s.DummyObjectSubSubclassWithoutStockpyleKeys(%s)" % (self.__module_name_for_dummy_objects, "zap=xyz")
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_verbose_lookup_keys(DummyObjectSubSubSubclass())
        expected_set = set([
            "stockpyle:%s.DummyObjectSubSubSubclass(%s)" % (self.__module_name_for_dummy_objects, "blarg=abc;foo=1")
            ])
        self.assertEqual(set(keys), expected_set)
    
    def test_generates_proper_terse_keys_list_when_nonpolymorphic(self):
        
        kvh = KeyValueHelper()
        
        # test dummy object
        keys = kvh.generate_all_terse_lookup_keys(DummyObject())
        expected_set = set([
            "stockpyle:%s.DummyObject(%s)" % (self.__module_name_for_dummy_objects, hash("bar=2;foo=1"))
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_terse_lookup_keys(DummyObjectSubclass())
        expected_set = set([
            "stockpyle:%s.DummyObjectSubclass(%s)" % (self.__module_name_for_dummy_objects, hash("zap=xyz"))
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_terse_lookup_keys(DummyObjectSubSubclassWithoutStockpyleKeys())
        expected_set = set([
            "stockpyle:%s.DummyObjectSubSubclassWithoutStockpyleKeys(%s)" % (self.__module_name_for_dummy_objects, hash("zap=xyz"))
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_terse_lookup_keys(DummyObjectSubSubSubclass())
        expected_set = set([
            "stockpyle:%s.DummyObjectSubSubSubclass(%s)" % (self.__module_name_for_dummy_objects, hash("blarg=abc;foo=1"))
            ])
        self.assertEqual(set(keys), expected_set)
    
    def test_generates_proper_verbose_keys_list_when_polymorphic(self):
        
        kvh = KeyValueHelper(polymorphic=True)
        
        # test dummy object
        keys = kvh.generate_all_verbose_lookup_keys(DummyObject())
        expected_set = set([
            "stockpyle:%s.DummyObject(%s)" % (self.__module_name_for_dummy_objects, "bar=2;foo=1")
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_verbose_lookup_keys(DummyObjectSubclass())
        expected_set = set([
            "stockpyle:%s.DummyObject(%s)" % (self.__module_name_for_dummy_objects, "bar=2;foo=1"),
            "stockpyle:%s.DummyObjectSubclass(%s)" % (self.__module_name_for_dummy_objects, "zap=xyz"),
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_verbose_lookup_keys(DummyObjectSubSubclassWithoutStockpyleKeys())
        expected_set = set([
            "stockpyle:%s.DummyObject(%s)" % (self.__module_name_for_dummy_objects, "bar=2;foo=1"),
            "stockpyle:%s.DummyObjectSubclass(%s)" % (self.__module_name_for_dummy_objects, "zap=xyz"),
            "stockpyle:%s.DummyObjectSubSubclassWithoutStockpyleKeys(%s)" % (self.__module_name_for_dummy_objects, "zap=xyz"),
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_verbose_lookup_keys(DummyObjectSubSubSubclass())
        expected_set = set([
            "stockpyle:%s.DummyObject(%s)" % (self.__module_name_for_dummy_objects, "bar=2;foo=1"),
            "stockpyle:%s.DummyObjectSubclass(%s)" % (self.__module_name_for_dummy_objects, "zap=xyz"),
            "stockpyle:%s.DummyObjectSubSubclassWithoutStockpyleKeys(%s)" % (self.__module_name_for_dummy_objects, "zap=xyz"),
            "stockpyle:%s.DummyObjectSubSubSubclass(%s)" % (self.__module_name_for_dummy_objects, "blarg=abc;foo=1"),
            ])
        self.assertEqual(set(keys), expected_set)
    
    def test_generates_proper_terse_keys_list_when_polymorphic(self):
        
        kvh = KeyValueHelper(polymorphic=True)
        
        # test dummy object
        keys = kvh.generate_all_terse_lookup_keys(DummyObject())
        expected_set = set([
            "stockpyle:%s.DummyObject(%s)" % (self.__module_name_for_dummy_objects, hash("bar=2;foo=1")),
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_terse_lookup_keys(DummyObjectSubclass())
        expected_set = set([
            "stockpyle:%s.DummyObject(%s)" % (self.__module_name_for_dummy_objects, hash("bar=2;foo=1")),
            "stockpyle:%s.DummyObjectSubclass(%s)" % (self.__module_name_for_dummy_objects, hash("zap=xyz")),
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_terse_lookup_keys(DummyObjectSubSubclassWithoutStockpyleKeys())
        expected_set = set([
            "stockpyle:%s.DummyObject(%s)" % (self.__module_name_for_dummy_objects, hash("bar=2;foo=1")),
            "stockpyle:%s.DummyObjectSubclass(%s)" % (self.__module_name_for_dummy_objects, hash("zap=xyz")),
            "stockpyle:%s.DummyObjectSubSubclassWithoutStockpyleKeys(%s)" % (self.__module_name_for_dummy_objects, hash("zap=xyz")),
            ])
        self.assertEqual(set(keys), expected_set)
        
        # test subclass
        keys = kvh.generate_all_terse_lookup_keys(DummyObjectSubSubSubclass())
        expected_set = set([
            "stockpyle:%s.DummyObject(%s)" % (self.__module_name_for_dummy_objects, hash("bar=2;foo=1")),
            "stockpyle:%s.DummyObjectSubclass(%s)" % (self.__module_name_for_dummy_objects, hash("zap=xyz")),
            "stockpyle:%s.DummyObjectSubSubclassWithoutStockpyleKeys(%s)" % (self.__module_name_for_dummy_objects, hash("zap=xyz")),
            "stockpyle:%s.DummyObjectSubSubSubclass(%s)" % (self.__module_name_for_dummy_objects, hash("blarg=abc;foo=1")),
            ])
        self.assertEqual(set(keys), expected_set)
    
        