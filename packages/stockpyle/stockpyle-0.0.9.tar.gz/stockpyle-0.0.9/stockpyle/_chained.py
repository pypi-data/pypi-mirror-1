from stockpyle._base import BaseStore


class ChainedStore(BaseStore):
    """Represents a chain of any arbitrary BaseStores.  Data will be written *through*
    all of these stores in order.  Data will be retrieved by attempting the first
    store, then the 2nd store, then the 3rd store, etc. until one of the stores returns
    a hit.  Hits are then stored forwards in all of the previous stores that had
    previously missed, so that next time an 'earlier' store can respond faster.
    
    Ideally, the stores would be ordered fastest-to-slowest.  A common use case for
    a ChainedStore is to have a persistent store with a multi-level cache front:
    
    fast_cache = ProcessMemoryStore()
    dist_cache = MemcacheStore(servers=["localhost:11711"])
    persistent_store = SqlAlchemyStore(uri="sqlite:///:memory:")
    
    chained_store = ChainedStore([fast_cache, dist_cache, persistent_store])
    """
    
    def __init__(self, stores=None):
        super(ChainedStore, self).__init__()
        if not stores:
            raise ValueError("you didn't specify any internal stores for this ChainedStore to operate on")
        self.__stores = stores
    
    def put(self, obj):
        
        # write-through
        for store in self.__stores:
            store.put(obj)
    
    def batch_put(self, objs):
        
        # write-through
        for store in self.__stores:
            store.batch_put(objs)
    
    def delete(self, obj):
        
        # delete-through
        for store in self.__stores:
            store.delete(obj)
    
    def batch_delete(self, objs):
        
        # delete-through
        for store in self.__stores:
            store.batch_delete(objs)
    
    def get(self, klass, key):
        
        # pull-through
        for i in range(0, len(self.__stores)):
            obj = self.__stores[i].get(klass, key)
            if obj:
                # we found it, pull it through all previous layers
                for previous_store in self.__stores[0:i]:
                    previous_store.put(obj)
                return obj
        
        # never found it
        return None
    
    def batch_get(self, klass, keys):
        
        # pull-through
        final_objects = [None for k in keys]
        for i in range(0, len(self.__stores)):
        
            # get as many hits as possible from this layer
            null_indices = [idx for idx in range(0, len(final_objects)) if final_objects[idx] is None]
            null_keys = [keys[null_idx] for null_idx in null_indices]
            new_objects = self.__stores[i].batch_get(klass, null_keys)
            nonnull_new_objects = []
            for null_idx, new_object in zip(null_indices, new_objects):
                final_objects[null_idx] = new_object
                if new_object:
                    nonnull_new_objects.append(new_object)
            
            # make sure any new objects are persisted in upper layers
            for previous_store in self.__stores[0:i]:
                previous_store.batch_put(nonnull_new_objects)
        
        # return whichever objects we found
        return final_objects
        