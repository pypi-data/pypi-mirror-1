from paver.defaults import Bunch

options(
    setup=Bunch(
        name="stockpyle",
        packages=["stockpyle"],
        version="0.0.1",
        license="BSD",
        author="Matt Pizzimenti",
        author_email="mjpizz+stockpyle@gmail.com",
        url="http://pypi.python.org/pypi/stockpyle/",
        install_requires = [],
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Software Development",
            "Topic :: System :: Distributed Computing",
        ],
        description="stockpyle is simple multi-layered storage and caching API",
        long_description='''\
Description
===========

stockpyle provides a simple way to set up a series of storage containers
for the purposes of creating simple write-through cache storage.

Usage
=====

Simplest script that sets up a two-level cache with memcached and local process memory::

    from stockpyle import MultiStore, MemcacheStore, ProcessMemoryStore
    
    # instantiate the MultiStore as a write-through cache
    pm = ProcessMemoryStore()
    mc = MemcacheStore(servers=["localhost:11711"])
    store = MultiStore([pm, mc])
    
    # declare a class that is unique for each (bar,zap) combination
    class Foo(object):
        
        __stockpyle_keys__ = [("bar", "zap")]
        
        def __init__(self, bar, zap):
            self.bar = bar
            self.zap = zap
    
    # create and save a Foo to the MultiStore
    obj = Foo(bar=444, zap=888)
    store.put(obj)
    
    # retrieve a Foo from the store, based on the (bar,zap) combination
    # this will hit the local memory cache first, and will avoid memcache
    # since the object is already cached there
    retrieved_obj = store.get(Foo, {"bar": 444, "zap": 888})

This example isn't that interesting, since we are using two caches.  Let's do one that supports
SQLAlchemy objects::

    from stockpyle.stores import MultiStore, SqlAlchemyStore, MemcacheStore, ProcessMemoryStore
    
    pm = ProcessMemoryStore()
    mc = MemcacheStore(servers=["localhost:11711"])
    sa = SqlAlchemyStore()
    store = MultiStore([pm, mc, sa])
    
    # store it, this will write it through the cache and into the database
    persistent_obj = MySqlAlchemyBackedClass()
    store.put(persistent_obj)

Note the ordering in the MultieStore declaration: the SQLAlchemyStore comes last, since it acts as the final persistence layer.
Subsequent gets will attempt process memory, then attempt memcache, and finally check the database.

Also, we can treat the process memory cache and the memcached differently by using different expirations.
For example, you may want process memory to expire quickly, but memcached to last a little longer since
you can actually keep it consistent across multiple machines. This example
forces Foo objects to be expired more aggressively from the local memory than memcached::

    pm = ProcessMemoryStore()
    mc = MemcacheStore(servers=["localhost:11711"])
    sa = SqlAlchemyStore()
    store = MultiStore([pm, mc])
    
    # Foo objects will last 60 seconds in local memory, and 5 minutes in memcache
    pm.configure(classes=[Foo], lifetime=60)
    mc.configure(classes=[Foo], lifetime=5*60)

Want to grab a bunch of objects?  Use batch_get::

    obj1, obj2, obj3 = store.batch_get(Foo, [
        {"foo": 111, "bar": 777},
        {"foo": 222, "bar": 888},
        {"foo": 333, "bar": 999},
        ])

Want to store a bunch of objects? Use batch_put::
    
    obj1 = Foo(111, 777)
    obj2 = Foo(222, 888)
    obj3 = Foo(333, 999)
    store.batch_put([obj1, obj2, obj3])

Deleting objects is easy (batch deletes coming soon)::

    store.delete(obj1)

You can use the Storable helper class to get class-level access to the storage APIs::

    from stockpyle import Storable
    
    
    class Bar(Storable):
        
        __stockpyle_keys__ = [("foo", "bar")]
        
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar
    
    
    # bind to a storage object
    store = ProcessMemoryStore()
    Bar.bind(store)
    
    # save an object
    obj = Bar(111, 777)
    obj.put()
    
    # get an object
    obj = Bar.get({"foo", "bar"})
    
    # delete an object
    obj.delete()
    
    # batched get
    obj1, obj2 = Bar.batched_get([
        {"foo": 111, "bar": 777},
        {"foo": 222, "bar": 888},
        ])
''',
        zip_safe = False,
        )
    )

@task
@needs(['generate_setup', 'minilib', 'setuptools.command.sdist'])
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
