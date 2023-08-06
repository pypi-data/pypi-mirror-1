from stockpyle._base import BaseStore


class AppEngineStore(object):
    """represents a storage container on the Google App Engine DataStore"""
        
    def put(self, obj):
        from google.appengine.ext import db
        if isinstance(obj, db.Model):
            db.put(obj)
        
    def batch_put(self, objs):
        from google.appengine.ext import db
        ds_objs = [o for o in objs if isinstance(o, db.Model)]
        db.put(ds_objs)
    
    def delete(self, obj):
        from google.appengine.ext import db
        if isinstance(obj, db.Model):
            db.delete(obj)
    
    def batch_delete(self, objs):
        from google.appengine.ext import db
        ds_objs = [o for o in objs if isinstance(o, db.Model)]
        db.delete(ds_objs)
    
    def get(self, klass, key):
        from google.appengine.ext import db
        if issubclass(klass, db.Model):
            query = db.Query(klass)
            for k,v in key.iteritems():
                query.filter("%s=" % k, v)
            return query.get()
    
    def batch_get(self, klass, keys):
        # TODO: is there a more efficient way?
        return [self.get(klass, k) for k in keys]
            
