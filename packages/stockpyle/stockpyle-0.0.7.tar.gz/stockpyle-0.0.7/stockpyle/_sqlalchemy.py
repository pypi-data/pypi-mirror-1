import threading
from stockpyle._base import BaseStore
try:
    from sqlalchemy.orm import EXT_CONTINUE, SessionExtension
    __HAS_SQLALCHEMY = True
except ImportError:
    __HAS_SQLALCHEMY = False
    

if __HAS_SQLALCHEMY:


    # SQLAlchemy is installed
    class StockpyleSessionExtension(SessionExtension):
        """If you have your own sessions, you can add this extension
        to force that session to synchronize objects with the given store"""
        
        def __init__(self, store):
            self.__store = store
            self.__operation_for_instance = {}
        
        def after_flush(self, session, flush_context):
            
            # deleted items must be deleted from the store
            for o in session.deleted:
                self.__operation_for_instance[o] = "delete"
            
            # new items must be put to the store
            for o in session.new:
                self.__operation_for_instance[o] = "put"
            
            # dirty items must be put to the store as well
            for o in session.dirty:
                self.__operation_for_instance[o] = "put"
                
            return EXT_CONTINUE
        
        def after_commit(self, session):
            
            # group operations by deletes/puts
            operation_map = {}
            for obj, operation in self.__operation_for_instance.iteritems():
                if operation not in operation_map:
                    operation_map[operation] = []
                operation_map[operation].append(obj)
            
            # do a batch delete for all deletes
            if "delete" in operation_map:
                self.__store.batch_delete(operation_map["delete"])
            
            # do a batch put for all puts
            if "put" in operation_map:
                self.__store.batch_put(operation_map["put"])
            
            # clear the operation cache, we're done
            self.__operation_for_instance = {}
            
            return EXT_CONTINUE
            
            
else:
    
    
    # SQLAlchemy is not installed
    class StockpyleSessionExtension(object):
        
        def __init__(self):
            raise StandardError("cannot use StockpyleSessionExtension without the SQLAlchemy module")


def _is_sqlalchemy_class(klass):
    """returns true if the given class is managed by SQLAlchemy"""
    # TODO: better way?
    return hasattr(klass, "_sa_class_manager")

def _is_sqlalchemy_object(obj):
    """returns true if the given object is managed by SQLAlchemy"""
    # TODO: better way?
    return hasattr(obj, "_sa_instance_state")


class SqlAlchemyStore(BaseStore):
    """Represents a storage target that can store any SQLAlchemy-mapped object.
    Non-SQLAlchemy objects will be ignored by this store."""
    
    engine = property(lambda self: self.__session.bind)
    """the engine that is connected to this session"""
    
    def __init__(self, uri=None, engine=None, session=None):

        super(SqlAlchemyStore, self).__init__()
        
        # get the session
        if session:
            if uri or engine:
                raise ValueError("you cannot specify a session, and also provide a connection string URI or engine")
            else:
                # we're good
                self.__session = session
        else:
            # no session, we have to make one
            # first we need to get the engine
            from sqlalchemy.orm import scoped_session, sessionmaker
            
            if uri and engine:
                raise ValueError("you can only provide either a connection string URI or an engine, not both")
            elif uri:
                from sqlalchemy import create_engine
                engine = create_engine(uri)
            elif not engine:
                raise ValueError("you must give a connection string URI, or an engine, or a bound session")
            
            # we can create the bound session now
            self.__session = sessionmaker(autoflush=True, bind=engine)()
    
    def put(self, obj):
        # only store SA objects
        if _is_sqlalchemy_object(obj):
            self._sa_put(obj)
        
    def batch_put(self, objs):
        # only store SA objects
        sa_objs = [o for o in objs if _is_sqlalchemy_object(o)]
        if sa_objs:
            self._sa_batch_put(sa_objs)
    
    def delete(self, obj):
        # only delete SA objects
        if _is_sqlalchemy_object(obj):
            self._sa_delete(obj)
    
    def batch_delete(self, objs):
        # only delete SA objects
        sa_objs = [o for o in objs if _is_sqlalchemy_object(o)]
        if sa_objs:
            self._sa_batch_delete(sa_objs)
    
    def get(self, klass, key):
        # only attempt to query SQAlchemy objects
        if _is_sqlalchemy_class(klass):
            return self._sa_get(klass, key)
        else:
            return None
    
    def batch_get(self, klass, keys):
        # only attempt to query SQAlchemy objects
        if _is_sqlalchemy_class(klass):
            return self._sa_batch_get(klass, keys)
        else:
            return [None for k in keys]
    
    def _sa_put(self, obj):
        from sqlalchemy.exceptions import InvalidRequestError
        try:
            self.__session.save_or_update(obj)
            self.__session.commit()
        except InvalidRequestError:
            # this is likely due to mismatched instances from cache
            self.__session.merge(obj)
            self.__session.commit()

    def _sa_batch_put(self, objs):
        from sqlalchemy.exceptions import InvalidRequestError
        
        # TODO: look at bulk_update?
        # save all in the session
        for obj in objs:
            self.__session.save_or_update(obj)
    
        # commit the session
        try:
            self.__session.commit()
        except InvalidRequestError:
            # this is likely due to mismatched instances from cache
            for obj in objs:
                self.__session.merge(obj)
            self.__session.commit()
    
    def _sa_delete(self, obj):
        from sqlalchemy.exceptions import InvalidRequestError
        try:
            self.__session.delete(obj)
            self.__session.commit()
        except InvalidRequestError:
            # this is likely due to mismatched instances from cache
            obj = self.__session.merge(obj)
            self.__session.delete(obj)
            self.__session.commit()
    
    def _sa_batch_delete(self, objs):
        from sqlalchemy.exceptions import InvalidRequestError

        # TODO: is there a bulk_delete in SA?
        try:
            for obj in objs:
                self.__session.delete(obj)
            self.__session.commit()
        except InvalidRequestError:
            # this is likely due to mismatched instances from cache
            for obj in objs:
                obj = self.__session.merge(obj)
                self.__session.delete(obj)
            self.__session.commit()
    
    def _sa_get(self, klass, key):
        return self.__session.query(klass).filter_by(**key).first()
    
    def _sa_batch_get(self, klass, keys):
        # FIXME: this is very inefficient, need to read up on the SA API a bit more
        return [self.get(klass, k) for k in keys]
        