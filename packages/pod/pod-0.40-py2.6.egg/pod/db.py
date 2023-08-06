import os
import sqlite3
import time
import exceptions
import inspect
import cPickle
import StringIO

import core

class current:
    global_db     = None
    time          = None
    
class PodDbError(exceptions.BaseException):
    pass

class PodLoadError(exceptions.BaseException):
    pass

class PodClassUndefined(exceptions.BaseException):
    pass

class Db(object):
    
    def __init__(self, file = ':memory:', remove = False, clear = False, connect = True, attach = None, chatty = False, very_chatty = False, use_full_table_name = True):
    
        # You must either: 
        #   1.  Never use 'attach', in which case you can only set one database connection
        #   2.  Always use 'attach', in which case you can have many databases which you must then 
        #       manually connect to objects. 
        if attach is None:
            if current.global_db is False:
                raise PodDbError, "You cannot create a global database connection after you've already created a database using the 'attach' parameter . . . "            
            elif current.global_db is not None:
                raise PodDbError, "You cannot create another database connection -- if you want to create more than one connection you'll need to set the 'attach' parameter"            
            current.global_db = self
        elif attach:
            if current.global_db:
                raise PodDbError, "You cannot create another database connection -- a global connection already created . . ."            
            current.global_db = False
            if isinstance(attach, (list,set)):
                for obj in attach:
                    self.attach_to_object(obj = obj)
            else:
                self.attach_to_object(obj = attach)
        
        # SETTINGS
        self.chatty      = chatty if very_chatty is False else True
        self.very_chatty = very_chatty
        # Can also be set in the class header under POD_USE_FULL_TABLE_NAME
        self.use_full_table_name = use_full_table_name   

        self.file       = file        
        self.mutants      = {}
        
        if remove:    
            self.remove()
        
        self.cache      = Cache(db = self)
        self.pickler    = Pickler(db = self)
        
        if self.file and connect:
            self.connect()
        else:
            self.connection = None
            self.cursor     = None    
                
        if clear: 
            self.clear()
            
        self.create_base_tables()
                
    def __getattr__(self, key):
        if key == 'store':
            self.store = Store(db = self)
            return self.store
        else:
            raise AttributeError, key 
           
    def create_base_tables(self):
        # This was moved to seperate function in order not to conflict with clear . . . 
        self.execute("CREATE TABLE IF NOT EXISTS pod_classes (id INTEGER PRIMARY KEY AUTOINCREMENT, cls_name TEXT UNIQUE, ctime INTEGER, mtime INTEGER, pod_types BINARY)")
        self.execute("CREATE UNIQUE INDEX IF NOT EXISTS cls_name_index ON pod_classes (cls_name)")
           
    def attach_to_object(self, obj):
        
        if inspect.ismodule(obj):
            classes = [cls for cls in obj.__dict__.values() if isinstance(cls, core.Meta)]                
        elif isinstance(obj, core.Meta):
            classes = [obj]
        else:
            raise PodDbError, "Unsupported type '" + str(obj) + "' . . . "

        for cls in classes:
            # You can't get or set attributes on Meta.Pod instances because you'll wake them up. 
            # Right now they are zombies . . . 
            db = object.__getattribute__(type.__getattribute__(cls, 'pod'), 'db')
            if db is None:
                object.__setattr__(type.__getattribute__(cls, 'pod'), 'db', self)
            elif db is not self:
                raise PodDbError, str(cls) + " already connected a database . . . "
                
    def connect(self):
        self.connection   = sqlite3.connect(self.file)
        if self.very_chatty:
            self.cursor       = Cursor(db = self) 
        else:
            self.cursor = self.connection.cursor()
        
    def remove(self):
        if self.is_connected():
            self.connection.close()
        if 'file' in self.__dict__ and os.path.isfile(self.file):
            os.remove(self.file)
    
    def clear(self):
        if self.chatty:
            print '*** Clearing database     ***'
        tables = [str(table[0]) for table in self.execute(query = 'select name from sqlite_master where type = ?', args = ('table',))]
        for table in tables:   
            if table != 'sqlite_sequence':
                if self.chatty:
                    print 'Clearing . . . dropping table ' + table
                self.execute(query = 'DROP TABLE ' + table)    
        self.commit(clear_cache = True, close = False)     
        self.vacuum()
        if self.chatty:
            print '*** End clearing database ***\n\n'

    def is_connected(self):
        return getattr(self, 'connection', None) is not None
                 
    def commit(self, clear_cache = False, close = False):
            
        # This resets mutable types so that they are saved if they were 'gotten'
        for inst,attrs in self.mutants.iteritems():
            cls_pod = type.__getattribute__(object.__getattribute__(inst,'__class__'), 'pod')
            for attr in attrs:
                cls_pod.inst_save_attr_to_db(inst,attr,object.__getattribute__(inst, attr))
                
        self.mutants.clear()
                
        self.connection.commit()
    
        if clear_cache:
            self.cache.clear_cache()
        
        if close:
            self.connection.close()
            
    def cancel(self, clear_cache = True, close = False):
        
        self.mutants.clear()
            
        self.connection.rollback()
        
        if clear_cache:
            self.cache.clear_cache()
        
        if close:
            self.connection.close()
                                     
    def vacuum(self):
        self.execute('VACUUM')
        
    def get_new_cursor(self):
        return Cursor(db = self)
        
    # Cursor passthroughs . . . 
    
    def execute(self, query, args = ()):
        return self.cursor.execute(query, args)
    
    def executemany(self, query, seq_of_args):
        return self.cursor.executemany(query, seq_of_args)
        
class Pickler(object):

    def __init__(self, db):
        self.db    = db
        self.cache = db.cache

    @staticmethod
    def persistent_id(value):
        return object.__getattribute__(value,'get_full_id')() if isinstance(value, core.Object) else None
    
    class PersistentLoad(object):
        
        def __init__(self, cache):
            self.cache = cache
        
        def __call__(self, id):
            id = id.split(':')
            return self.cache.get_inst(cls_id = int(id[0]), inst_id = int(id[1]))
          
    @staticmethod  
    def dump(value):
        
        if value is None:
            return None
        else:
            if isinstance(value, core.Object):
                return 'o' + object.__getattribute__(value,'get_full_id')()
            else:
                vclass = getattr(value, '__class__', None)
                if vclass is str:
                    return 's' + value
                elif vclass is int:
                    return 'i' + str(value)
                elif vclass is float:
                    return 'f' + str(value)
                elif value is True:
                    return '1'
                elif value is False:
                    return '0'
                else:        
                    return 'x' + Pickler.cdump(value)    
    
    @staticmethod
    def cdump(value):
        src                     = StringIO.StringIO()      
        pickler                 = cPickle.Pickler(src)
        pickler.persistent_id   = Pickler.persistent_id
        pickler.dump(value)
        return src.getvalue()

    @staticmethod
    def bdump(value):
        src                     = StringIO.StringIO()             
        pickler                 = cPickle.Pickler(src, True)
        pickler.persistent_id   = Pickler.persistent_id    
        pickler.dump(value)        
        return sqlite3.Binary(src.getvalue())

    def load(self, value):
        if value is None:
            return None
        else:
            first = value[0]
            if first == 'o':
                id = value[1:].split(':')
                return self.cache.get_inst(cls_id = int(id[0]), inst_id = int(id[1]))
            elif first == 's':
                return str(value[1:])
            elif first == 'i':
                return int(value[1:])
            elif first == 'f':
                return float(value[1:])
            elif first == '1': 
                return True
            elif first == '0':
                return False
            elif first == 'x':
                return self.cload(value[1:])
            else:
                raise PodLoadError, "Unsupported type '" + str(value) + "' . . . "

    def cload(self, value): 
        unpickler                 = cPickle.Unpickler(StringIO.StringIO(str(value)))
        unpickler.persistent_load = Pickler.PersistentLoad(cache = self.cache)
        return unpickler.load()    

class Cursor(object):

    def __init__(self, db):
        self.db = db
        self.very_chatty = db.very_chatty
        self.cursor = db.connection.cursor()

    def __iter__(self):
        return self.cursor.__iter__()

    def __getattr__(self, attr):
        return self.cursor.__getattribute__(attr)

    def execute(self, query, args = ()):
        if self.very_chatty:
            self._sql_count = getattr(self, '_sql_count', -1) + 1
            print "\tSQL COMMAND #" + str(self._sql_count) + ": \t" + query
            print "\tSQL VALUES:  \t\t" + str(args) + '\n'
        return self.cursor.execute(query, args)
    
    def executemany(self, query, seq_of_args):
        if self.very_chatty:
            self._sql_count = getattr(self, '_sql_count', -1) + 1
            print "\tSQL COMMAND #" + str(self._sql_count) + ": \t" + query
            print "\tSQL VALUES:  \t\t" + str(seq_of_args) + '\n'
        return self.cursor.executemany(query, seq_of_args)
        
class Cache(object):
    
    def __init__(self, db):
        
        self.db          = db        
        self.class_pods  = {}

    def get_inst(self, cls_id, inst_id): 

        cls_pod = self.class_pods.get(cls_id, None)
        
        if cls_pod is None:
            return core.Undefined(id = (cls_id, inst_id), cursor = self.db.cursor)
        else:
            return cls_pod.inst_get_inst_by_id(inst_id = inst_id, zombie = True)
    
    def clear_cache(self):            
        for cls_pod in self.class_pods.itervalues():
            cls_pod.cache.clear()
            cls_pod.zombies.clear()
    
""" STORE """  
class Store(object):
    
    def __init__(self, db, prefix = "pod_db_store_"):
        object.__setattr__(self, 'db', db)
        object.__setattr__(self, 'prefix', prefix)
        
        self.db.execute("CREATE TABLE IF NOT EXISTS pod_store_all (key_name TEXT UNIQUE PRIMARY KEY, value BINARY)")
        self.db.execute("CREATE UNIQUE INDEX IF NOT EXISTS _key_name_index ON pod_store_all (key_name)")

    def __getitem__(self, key):
        result = self.db.execute(query = "SELECT value FROM pod_store_all WHERE key_name=?", args = (self.prefix + key,)).fetchall()
        if len(result) == 1:
            return self.db.pickler.load(result[0][0])
        else:
            raise PodDbError, "The key '" + key + "' was not found in the database store all . . . "

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __setitem__(self, key, value):
        self.db.execute(query = "INSERT OR REPLACE INTO pod_store_all (key_name,value) VALUES (?,?)", args = (self.prefix + key, self.db.pickler.dump(value),))
        
    def __setattr__(self, key, value):
        return self.__setitem__(key, value)     

