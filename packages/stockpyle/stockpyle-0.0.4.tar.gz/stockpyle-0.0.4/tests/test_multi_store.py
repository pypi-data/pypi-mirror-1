from unittest import TestCase
from time import sleep
from collections import defaultdict
from tests.helpers import CountingStoreWrapper
from tests.fixture_store import StoreFixture, ExpiringStoreFixture
from stockpyle._multi import MultiStore
from stockpyle._procmem import ProcessMemoryMemcacheClient, ProcessMemoryStore
from stockpyle._memcache import MemcacheStore


class Foobar(object):
    
    __stockpyle_keys__ = [("foo", "bar"), ("bar", "zap"), "zap"]
    
    def __init__(self, foo, bar, zap):
        self.foo = foo
        self.bar = bar
        self.zap = zap
    
    def __eq__(self, other):
        return other and (other.foo, other.bar == self.foo, self.bar)


class MultiStoreWithLocalAndMemcacheTestCase(StoreFixture, ExpiringStoreFixture, TestCase):
    
    store = property(lambda self: self.__store)
    
    def setUp(self):
        local = ProcessMemoryStore()
        mc = MemcacheStore(client=ProcessMemoryMemcacheClient())
        self.__store = MultiStore([local, mc])


class MultiStoreWriteThroughTestCase(TestCase):
    
    store = property(lambda self: self.__store)
    
    def setUp(self):
        self.__local = CountingStoreWrapper(ProcessMemoryStore())
        self.__mc = CountingStoreWrapper(MemcacheStore(client=ProcessMemoryMemcacheClient()))
        self.__store = MultiStore([self.__local, self.__mc])
    
    def test_after_writethrough_gets_from_only_local(self):
        obj = Foobar(1,2,3)
        
        self.__store.put(obj)
        
        obj_r = self.__store.get(Foobar, {"foo": 1, "bar": 2})
        self.assertEqual(obj_r, obj)
        
        self.assertEqual(self.__local.counts["get"], 1)
        self.assertEqual(self.__mc.counts["get"], 0)
        
    def test_can_expire_earlier_in_certain_caches(self):
        
        # lasts 1 second longer in memcached
        self.__local.configure(classes=[Foobar], lifetime=1)
        self.__mc.configure(classes=[Foobar], lifetime=2)
        
        obj = Foobar(1,2,3)
        
        self.__store.put(obj)
        
        obj_r = self.__store.get(Foobar, {"foo": 1, "bar": 2})
        self.assertEqual(obj_r, obj)
        
        self.assertEqual(self.__local.counts["get"], 1)
        self.assertEqual(self.__mc.counts["get"], 0)
        
        # now wait for the local cache to expire
        sleep(1)
        
        obj_r = self.__store.get(Foobar, {"foo": 1, "bar": 2})
        self.assertEqual(obj_r, obj)
        
        self.assertEqual(self.__local.counts["get"], 2)
        self.assertEqual(self.__mc.counts["get"], 1)
        
        # finally wait for all caches to expire
        sleep(2)
        
        obj_r = self.__store.get(Foobar, {"foo": 1, "bar": 2})
        self.assertEqual(obj_r, None, "object should be completely gone now")
        
        self.assertEqual(self.__local.counts["get"], 3)
        self.assertEqual(self.__mc.counts["get"], 2)

