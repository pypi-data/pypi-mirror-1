import threading
from stockpyle._base import BaseStore
try:
    from sqlalchemy.orm import EXT_CONTINUE, MapperExtension
    _has_sqlalchemy = True
except ImportError:
    _has_sqlalchemy = False
    

if _has_sqlalchemy:

    # SQLAlchemy is installed
    class SqlAlchemyStoreExtension(MapperExtension):
    
        def __get_store(self):
            if callable(self.__store):
                return self.__store()
            else:
                return self.__store
                
        def __init__(self, store=None):
            self.__store = store

        def after_update(self, mapper, connection, instance):
            _do_sqlalchemy_operation(objs=[instance], operation=lambda: self.__get_store().put(instance))
            return EXT_CONTINUE

        def after_delete(self, mapper, connection, instance):
            _do_sqlalchemy_operation(objs=[instance], operation=lambda: self.__get_store().delete(instance))
            return EXT_CONTINUE

        def after_insert(self, mapper, connection, instance):
            _do_sqlalchemy_operation(objs=[instance], operation=lambda: self.__get_store().put(instance))
            return EXT_CONTINUE
            
            
else:
    
    # SQLAlchemy cannot be installed
    class SqlAlchemyStoreExtension(object):
        
        def __init__(self):
            raise StandardError("cannot use SqlAlchemyStoreExtension without SQLAlchemy")


_threadlocal = threading.local()

def _get_threadlocal():
    try:
        return _threadlocal.__stockpyle__
    except AttributeError:
        _threadlocal.__stockpyle__ = {}
        return _threadlocal.__stockpyle__

def _do_sqlalchemy_operation(objs, operation):
    doing_operation = bool(True in [_get_threadlocal().get(o, False) for o in objs])
    if not doing_operation:
        # mark these objects as being updated
        for o in objs:
            _get_threadlocal()[o] = True
        try:
            operation()
        finally:
            # unmark these objects as being updated
            for o in objs:
                if o in _get_threadlocal():
                    del _get_threadlocal()[o]
    
def _is_sqlalchemy_class(klass):
    # TODO: better way?
    return hasattr(klass, "_sa_class_manager")

def _is_sqlalchemy_object(obj):
    # TODO: better way?
    return hasattr(obj, "_sa_instance_state")


class SqlAlchemyStore(BaseStore):
    
    def __init__(self):
        from sqlalchemy.orm import scoped_session, sessionmaker
        super(SqlAlchemyStore, self).__init__()
        self.__session = scoped_session(sessionmaker(autoflush=True))
    
    def put(self, obj):
        from sqlalchemy.exceptions import InvalidRequestError
        
        if _is_sqlalchemy_object(obj):
            
            def put():
                try:
                    self.__session.save_or_update(obj)
                    self.__session.commit()
                except InvalidRequestError:
                    # this is likely due to mismatched instances from cache
                    self.__session.merge(obj)
                    self.__session.commit()
            
            _do_sqlalchemy_operation(objs=[obj], operation=put)
        
    def batch_put(self, objs):
        from sqlalchemy.exceptions import InvalidRequestError
        
        sa_objs = [o for o in objs if _is_sqlalchemy_object(o)]
        
        def batch_put():
            # save all in the session
            for obj in sa_objs:
                self.__session.save_or_update(obj)
            
            # commit the session
            try:
                self.__session.commit()
            except InvalidRequestError:
                # this is likely due to mismatched instances from cache
                for obj in sa_objs:
                    self.__session.merge(obj)
                self.__session.commit()
        
        _do_sqlalchemy_operation(objs=sa_objs, operation=batch_put)
    
    def delete(self, obj):
        from sqlalchemy.exceptions import InvalidRequestError
        
        local_obj = [obj]
        
        def delete():
            
            obj = local_obj[0]
            
            try:
                self.__session.delete(obj)
                self.__session.commit()
            except InvalidRequestError:
                # this is likely due to mismatched instances from cache
                obj = self.__session.merge(obj)
                self.__session.delete(obj)
                self.__session.commit()
                self.__session.commit()
        
        _do_sqlalchemy_operation(objs=[obj], operation=delete)
    
    def get(self, klass, key):
        if _is_sqlalchemy_class(klass):
            return self.__session.query(klass).filter_by(**key).first()
        else:
            return None
    
    def batch_get(self, klass, keys):
        # FIXME: this is very inefficient, need to read up on the SA API a bit more
        if _is_sqlalchemy_class(klass):
            return [self.get(klass, k) for k in keys]
        else:
            return [None for k in keys]
