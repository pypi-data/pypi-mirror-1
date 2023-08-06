from urlparse import urlparse
import httplib
import datetime
import copy
import urllib

import simplejson

class SchemeError(Exception): pass

class HTTPInteraction(object):
    def __init__(self, uri):
        self.url = urlparse(uri)
    def __getattr__(self, name):
        if name.upper() in ['HEAD', 'GET', 'PUT', 'DELETE', 'POST']:
            return lambda path, body=None, headers=None : self.request(name.upper(), path, body, headers)
    def request(self, method, path, body=None, headers=None):
        # Create connection class
        if self.url.scheme == 'http':
            connection = httplib.HTTPConnection(self.url.netloc)
        elif self.url.scheme == 'https':
            connection = httplib.HTTPSConnection(self.url.netloc)
        else:
            raise SchemeError(self.url.scheme+' is not a valid scheme.')
        
        if headers is None:
            headers = {'content-type':'application/json', 
                       'user-agent':'pouch-0.1pre'}
        
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        
        response.body = response.read()
        
        return response
        
def make_path(dbname, *args):
    return '/'+'/'.join([dbname]+list(args))

class Connection(object):
    """Handles the connection to a given server."""
    def __init__(self, uri):
        self.http = HTTPInteraction(uri)
        
    def create_db(self, name):
        response = self.http.put('/'+name.lower())
        assert simplejson.loads(response.body)['ok']
        return Database(self, name.lower())
    
    def delete_db(self, name):
        response = self.http.delete('/'+name.lower())
        assert simplejson.loads(response.body)['ok']
        
    def db_info(self, name):
        response = self.http.get('/'+name.lower())
        return simplejson.loads(response.body)
    
class Database(object):
    "Handles interaction with a single couchdb database."
    def __init__(self, name, connection=None):
        self.name = name
        if connection is None:
            self.connection = GLOBAL_CONNECTION
        else:
            self.connection = connection
        self.views = Views(self)
        
    def create_doc(self, obj):
        response = self.connection.http.post('/'+self.name, body=simplejson.dumps(obj))
        assert response.status == 201
        response_obj = simplejson.loads(response.body)
        assert response_obj['ok']
        return response_obj
    
    def update_doc(self, obj):
        response = self.connection.http.put(make_path(self.name, obj['_id']), body=simplejson.dumps(obj))
        assert response.status == 201
        response_obj = simplejson.loads(response.body)
        assert response_obj['ok']
        return response_obj
    
    def get_doc(self, _id):
        return simplejson.loads(self.connection.http.get(make_path(self.name, _id)).body)

ALL_MODEL_CLASSES = {}

GLOBAL_CONNECTION = None
GLOBAL_DB = None

def set_globals(uri, dbname):
    global GLOBAL_CONNECTION
    global GLOBAL_DB
    GLOBAL_CONNECTION = Connection(uri)
    GLOBAL_DB = Database(dbname, GLOBAL_CONNECTION) 
    for cls in ALL_MODEL_CLASSES.values():
        cls.db = GLOBAL_DB

class ModelMeta(type):
    def __init__(cls, name, bases, attrdict):
        
        if cls.__name__ != 'Model':
            super(ModelMeta, cls).__init__(name, bases, dict([(k,attrdict[k],) for k in ['__module__']]))
            assert cls.__name__ not in ALL_MODEL_CLASSES.keys()
            
            cls.__restrictions__ = dict([(k,v,) for k, v in attrdict.items() if not k.startswith('__') and type(v).__name__ != 'function'])
            
            assert cls.__name__ not in ALL_MODEL_CLASSES.keys()        
            cls.type = cls.__name__
            ALL_MODEL_CLASSES[cls.type] = cls
        else:
            super(ModelMeta, cls).__init__(name, bases, attrdict)
    
class Model(object):
    __metaclass__ = ModelMeta
    db = GLOBAL_DB
    
    __reserved_words__ = ['db', 'save']
    
    def __init__(self, **kwargs):
        if self.db is None:
            db = GLOBAL_DB
        else:
            db = self.db
        self.__dict__ = {}
        self.db = db
        for k, v in self.__restrictions__.items():
            if hasattr(v, 'auto_add') and v.auto_add is True:
                kwargs[k] = v.auto()
            if hasattr(v, 'cast') and k in kwargs.keys():
                kwargs[k] = v.cast(kwargs[k])
        for key, value in kwargs.items():
            self.__setattr__(key, value)
        if not kwargs.has_key('type'):
            self.__dict__['type'] = self.type
        
    def __setattr__(self, key, value):
        if key.startswith('__'):
            return object.__setattr__(self, key, value)
        if self.__restrictions__.has_key(key):
            self.__restrictions__[key].validate(value)
        self.__dict__[key] = value
        
    def __str__(self):
        return self.__class__.__name__+'(pouch.Model): '+str(self.__dict__)
                
    def save(self):
        upload_dict = copy.copy(self.__dict__)
        for r in self.__reserved_words__:
            upload_dict.pop(r, None)
        for key in self.__restrictions__.keys():
            if upload_dict.has_key(key):
                upload_dict[key] = self.__restrictions__[key].marshall(upload_dict[key])
        if hasattr(self, '_id'):
            response_dict = self.db.update_doc(upload_dict)
        else:
            response_dict = self.db.create_doc(upload_dict)
        self.__dict__.update({'_id':response_dict['id'], '_rev':response_dict['rev']})
    
    @classmethod
    def get(cls, _id):
        db = cls.db or GLOBAL_DB
        return cls(**dict([(str(k),v,) for k,v in db.get_doc(_id).items()]))
    
    
    def __cmp__(self, other):
        if other.__dict__ == self.__dict__:
            return 0

class ModelRestrictionValidationError(Exception): pass
            
class Restriction(object):
    def validate(self, value):
        if hasattr(self, 'type'):
            if type(value) != self.type:
                raise ModelRestrictionValidationError('Value of '+str(value)+' is not '+self.type.__name__)
            else:
                return
        return
    
    marshall = lambda self, value : value

class LooserRestriction(object):
    def validate(self, value):
        if hasattr(self, 'type'):
            try:
                self.type(value)
            except:
                raise ModelRestrictionValidationError('Value of '+str(value)+' is not '+self.type.__name__)
            return
        return
        
    marshall = lambda self, value : self.type(value)
     
class Unicode(LooserRestriction):
    type = unicode
class Int(Restriction):
    type = int
class Float(Restriction):
    type = float
class List(LooserRestriction):
    type = list
class Dict(Restriction):
    type = dict
class Bool(Restriction):
    type = bool
class DateTime(Restriction):
    def __init__(self, auto_now=False):
        self.auto_now = auto_now
        self.auto_add = auto_now
    type = datetime.datetime
    def marshall(self, value):
        return value.isoformat()
    def auto(self):
        return datetime.datetime.now()

class View(object):
    def __init__(self, db, path):
        self.db, self.path = db, path
    def __call__(self, **kwargs):
        for k, v in kwargs.items():
            if type(v) is bool:
                kwargs[k] = str(v).lower()
            if k in ['key', 'startkey', 'endkey']:
                kwargs[k] = simplejson.dumps(v)
        query_string = urllib.urlencode(kwargs)
        if len(query_string) is not 0:
            path = self.path + '?' + query_string
        else:
            path = self.path
        result = self.db.connection.http.get(path).body
        return simplejson.loads(result)

class DesignDocument(object):
    def __init__(self, db, path):
        self.db, self.path = db, path
    def __getattr__(self, name):
        return View(self.db, self.path + '/' + name)

class Views(object): 
    def __init__(self, db):
        self.db = db
    def __getattr__(self, name):
        return DesignDocument(self.db, make_path(self.db.name, '_view', name))
