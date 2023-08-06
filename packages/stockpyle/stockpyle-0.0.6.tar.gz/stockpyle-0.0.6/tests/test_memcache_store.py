from unittest import TestCase
from tests.fixture_store import StoreFixture, ExpiringStoreFixture
from tests.mocks import MockMemcacheClient
from stockpyle._memcache import MemcacheStore


class MemcacheStoreTestCase(StoreFixture, ExpiringStoreFixture, TestCase):
    
    store = property(lambda self: self.__mc)
    
    def setUp(self):
        self.__mc = MemcacheStore(client=MockMemcacheClient(), lifetime_cb=self.lifetime_cb)
    
    def test_must_specify_client_or_servers(self):
        self.assertRaises(ValueError, lambda: MemcacheStore())
        self.assertRaises(ValueError, lambda: MemcacheStore(client=MockMemcacheClient(), servers=["localhost:8080"]))
        try:
            MemcacheStore(servers=["localhost:8080"])
        except Exception, e:
            self.fail("should be able to create client against server list (%s)" % str(e))