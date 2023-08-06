from unittest import TestCase
from sqlalchemy import Column
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from tests.helpers import CountingStoreWrapper
from tests.fixture_store import StoreFixture, DeclarativeBase
from stockpyle._multi import MultiStore
from stockpyle._procmem import ProcessMemoryStore
from stockpyle._sqlalchemy import SqlAlchemyStore, SqlAlchemyStoreExtension


class SqlAlchemyStoreTestCase(StoreFixture, TestCase):
    
    store = property(lambda self: self.__store)
    
    def setUp(self):
        DeclarativeBase.metadata.create_all()
        self.__store = SqlAlchemyStore()
        
    def tearDown(self):
        DeclarativeBase.metadata.drop_all()


class MultiStoreWithSqlAlchemyTestCase(TestCase):
    
    def setUp(self):        
        DeclarativeBase.metadata.create_all()
        self.__lm = CountingStoreWrapper(ProcessMemoryStore())
        self.__sa = CountingStoreWrapper(SqlAlchemyStore())
        self.__store = MultiStore([self.__lm, self.__sa])

    def tearDown(self):
        DeclarativeBase.metadata.drop_all()
    
    def test_local_memory_updated_even_when_object_updated_outside_stockpyle(self):
        
        # create an auto-updating store
        store = self.__store
        
        
        class Bazbot(DeclarativeBase):
    
            __tablename__ = "bazbots"
            __mapper_args__ = {"extension": SqlAlchemyStoreExtension()}
            __stockpyle_store__ = property(lambda self: store)
    
            zap = Column(Integer, primary_key=True)
            foo = Column(Integer)
            bar = Column(Integer)
    
            __stockpyle_keys__ = [("foo", "bar"), ("bar", "zap"), "zap"]
    
            def __init__(self, foo, bar, zap):
                self.foo = foo
                self.bar = bar
                self.zap = zap
    
            def __eq__(self, other):
                return other and (other.foo, other.bar == self.foo, self.bar)
        
        
        # add bazbot to the schema
        DeclarativeBase.metadata.create_all()
        
        # create a separate SA session
        session = scoped_session(sessionmaker(autoflush=True))
        
        # create and do a sanity check
        obj = Bazbot(1,2,3)
        self.__store.put(obj)
        
        obj_r = self.__store.get(Bazbot, {"zap": 3})
        self.assertEqual(obj_r, obj)
        
        self.assertEqual(self.__lm.counts["get"], 1)
        self.assertEqual(self.__sa.counts["get"], 0)
        
        # now, update obj outside of stockpyle
        sa_obj = session.query(Bazbot).filter_by(zap=3).first()
        sa_obj.bar = 555
        session.save_or_update(sa_obj)
        
        # the commit should cause the cache to be updated
        self.assertEqual(self.__lm.counts["put"], 1)
        session.commit()
        self.assertEqual(self.__lm.counts["put"], 2)
        
        obj_r = self.__store.get(Bazbot, {"zap": 3})
        self.assertEqual(obj_r, obj)
        
        # we still haven't ever done a SA persistent get
        self.assertEqual(self.__lm.counts["get"], 2)
        self.assertEqual(self.__sa.counts["get"], 0)
    