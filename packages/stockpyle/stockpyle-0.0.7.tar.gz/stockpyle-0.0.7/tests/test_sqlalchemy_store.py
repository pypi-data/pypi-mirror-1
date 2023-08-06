try:
    import sqlalchemy
    __HAVE_SA = True
except ImportError:
    import sys
    print >> sys.stderr, "\n*** warning: skipping optional SQLAlchemy tests, you don't have the module (http://pypi.python.org/pypi/SQLAlchemy)"
    __HAVE_SA = False


if __HAVE_SA:

    from unittest import TestCase
    from sqlalchemy import Column
    from sqlalchemy.types import Integer, String
    from sqlalchemy.orm import sessionmaker
    from tests.helpers import CountingStoreWrapper
    from tests.fixture_store import StoreFixture, DeclarativeBase, Foobar
    from stockpyle._chained import ChainedStore
    from stockpyle._procmem import ProcessMemoryStore
    from stockpyle._sqlalchemy import SqlAlchemyStore, StockpyleSessionExtension


    class SqlAlchemyStoreTestCase(StoreFixture, TestCase):
    
        store = property(lambda self: self.__store)
    
        def setUp(self):
            self.__store = SqlAlchemyStore(uri="sqlite:///:memory:")
            DeclarativeBase.metadata.create_all(bind=self.__store.engine)
        
        def tearDown(self):
            DeclarativeBase.metadata.drop_all(bind=self.__store.engine)
        
        def test_can_delete_retrieved_object_from_external_session(self):
        
            obj = Foobar(1,2,3)
            self.store.put(obj)
        
            # get using a sqlalchemy session
            session = sessionmaker(autoflush=True, bind=self.__store.engine)()
            obj_r = session.query(Foobar).first()
            self.assertEqual(obj_r, obj)
        
            # now delete the obj through the store
            self.store.delete(obj_r)
        
            # store should say empty
            obj_r = self.store.get(Foobar, {"foo": 1, "bar": 2})
            self.assertEqual(obj_r, None)
        
            # raw db request should say empty
            obj_r = session.query(Foobar).first()
            self.assertEqual(obj_r, None)
        
        def test_can_do_batch_delete_on_retrieved_objects_from_external_session(self):
        
            obj1 = Foobar(1,2,3)
            obj2 = Foobar(4,5,6)
        
            self.store.put(obj1)
            self.store.put(obj2)
        
            # get using a sqlalchemy session
            session = sessionmaker(autoflush=True, bind=self.__store.engine)()
            objs = session.query(Foobar).all()
            self.assertEqual(len(objs), 2)
        
            # verify we got the same objects out
            obj1_r, obj2_r = tuple(objs)
            self.assertEqual(obj1_r, obj1)
            self.assertEqual(obj2_r, obj2)
        
            # now delete them
            # session.expunge(obj1_r)
            # session.expunge(obj2_r)
            self.store.batch_delete([obj1_r, obj2_r])
        
            obj1_r, obj2_r = self.store.batch_get(Foobar, [
                {"foo": 1, "bar": 2}, #obj1
                {"foo": 4, "bar": 5}, #obj2
                ])
        
            self.assertEqual(obj1_r, None)
            self.assertEqual(obj2_r, None)


    class ChainedStoreWithSqlAlchemyTestCase(TestCase):
    
        def setUp(self):
            self.__lm = CountingStoreWrapper(ProcessMemoryStore())
            self.__sa = CountingStoreWrapper(SqlAlchemyStore(uri="sqlite:///:memory:"))
            self.__store = ChainedStore([self.__lm, self.__sa])
            DeclarativeBase.metadata.create_all(bind=self.__sa.engine)

        def tearDown(self):
            DeclarativeBase.metadata.drop_all(bind=self.__sa.engine)
    
        def test_local_memory_updated_even_when_object_updated_outside_stockpyle(self):
        
            # create an auto-updating store
            store = self.__store
        
        
            class Bazbot(DeclarativeBase):
    
                __tablename__ = "bazbots"
            
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
            DeclarativeBase.metadata.create_all(bind=self.__sa.engine)
        
            # create a separate SA session
            ext = StockpyleSessionExtension(self.__lm)
            session = sessionmaker(autoflush=True, extension=ext, bind=self.__sa.engine)()
        
            # create and do a sanity check
            obj = Bazbot(1,2,3)
            self.assertEqual(self.__sa.counts["put"], 0)
            self.__store.put(obj)
            self.assertEqual(self.__sa.counts["put"], 1)
        
            obj_r = self.__store.get(Bazbot, {"zap": 3})
            self.assertEqual(obj_r, obj)
        
            self.assertEqual(self.__lm.counts["get"], 1)
            self.assertEqual(self.__sa.counts["get"], 0)
        
            # now, update obj outside of stockpyle
            sa_obj = session.query(Bazbot).filter_by(zap=3).first()
            sa_obj.bar = 555
            session.save_or_update(sa_obj)
        
            # the commit should cause the cache to be updated
            self.assertEqual(self.__lm.counts["batch_put"], 0)
            print "about to commit..."
            session.commit()
            print "committed..."
            self.assertEqual(self.__lm.counts["batch_put"], 1)
            self.assertEqual(self.__sa.counts["put"], 1)
        
            obj_r = self.__store.get(Bazbot, {"zap": 3})
            self.assertEqual(obj_r, obj)
        
            # we still haven't ever done a SA persistent get
            self.assertEqual(self.__lm.counts["get"], 2)
            self.assertEqual(self.__sa.counts["get"], 0)
