import os
import sys
import sqlite3
import time
import exceptions
import inspect
import cPickle
import StringIO

import core

class register:
    global_db      = None
    pods_to_attach = {}
    
class PodDbError(exceptions.BaseException):
    pass

class PodLoadError(exceptions.BaseException):
    pass

class PodClassUndefined(exceptions.BaseException):
    pass

class PodStoreError(exceptions.BaseException):
    pass

class Db(object):
    
    def __init__(self, file = ':memory:', remove = False, clear = False, attach = None, chatty = False, very_chatty = False, dynamic_index = False, use_full_table_name = True, activate_on_attach = True ):
    
        # SETTINGS
        self.chatty              = chatty if very_chatty is False else True
        self.very_chatty         = very_chatty
        # Can also be set in the class header under POD_DYNAMIC_INDEX, POD_ACTIVATE_ON_ATTACH, POD_USE_FULL_TABLE_NAME
        self.dynamic_index       = dynamic_index
        self.use_full_table_name = use_full_table_name   
        self.activate_on_attach  = activate_on_attach

        self.file       = file        
        self.mutables   = {}

        if remove:    
            self.remove()

        self.connection   = sqlite3.connect(self.file)
        if self.very_chatty:
            self.cursor  = Cursor(db = self) 
        else:
            self.cursor  = self.connection.cursor()

        self.cache      = Cache(db = self)
        self.pickler    = Pickler(db = self)
        
        if clear: 
            self.clear()
            
        self.sql_create_base_tables()
                
        # You must either: 
        #   1.  Never use 'attach', in which case you can only set one database connection
        #   2.  Always use 'attach', in which case you can have many databases which you must then 
        #       manually connect to objects. 
        if attach is None:
            if register.global_db is False:
                raise PodDbError, "You cannot create a global database connection after you've already created a database using the 'attach' parameter . . . "            
            elif register.global_db is not None:
                raise PodDbError, "You cannot create another database connection -- if you want to create more than one connection you'll need to set the 'attach' parameter"            
            register.global_db = self         
            for table_name,cls_pod in register.pods_to_attach.iteritems():
                cls_pod.attach_to_db(db = self)   
            register.pods_to_attach.clear()           
        elif attach is not None:
            if register.global_db:
                raise PodDbError, "You cannot create another database connection -- a global connection already created . . ."            
            register.global_db = False
            if isinstance(attach, (list,set,tuple)):
                for obj in attach:
                    self.attach(obj = obj)
            else:
                self.attach(obj = attach)
      
    def __getattr__(self, key):
        if key == 'store':
            self.store = Store(db = self)
            return self.store
        else:
            raise AttributeError, key 
           
    def attach(self, obj):
        """ Takes either a module and finds root levels classes or a core.Meta class directly """
        if inspect.ismodule(obj):
            classes = [cls for cls in obj.__dict__.values() if isinstance(cls, core.Meta)]                
        elif isinstance(obj, core.Meta):
            classes = [obj]
        elif isinstance(obj, (list,set,tuple,frozenset)):
            classes = [o for o in obj if isinstance(o, core.Meta)]
        else:
            raise PodDbError, "Unsupported type '" + str(obj) + "' . . . "

        for cls in classes:
            type.__getattribute__(cls, 'pod').attach_to_db(db = self)
                
    def remove(self):
        if self.is_connected():
            self.connection.close()
        if 'file' in self.__dict__ and os.path.isfile(self.file):
            os.remove(self.file)
    
    def clear(self):
        if self.chatty:
            print '*** Clearing database     ***'
        for table in self.get_table_list():   
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
        for inst,value in self.mutables.iteritems():
            cls_pod = type.__getattribute__(object.__getattribute__(inst,'__class__'), 'pod')
            dict = object.__getattribute__(inst, '__dict__')
            for attr,pair in value.iteritems():
                if attr in dict:
                    col,old_value = pair[0],pair[1]
                    new_value     = cls_pod.sql_pickle_dump(dict[attr])
                    if new_value[0] == 'x' and old_value != new_value:
                        if col:
                            self.cursor.execute('UPDATE ' + cls_pod.table + ' SET ' + attr + '=? WHERE id=?', (new_value, inst.id,))
                        else:
                            self.cursor.execute('INSERT OR REPLACE INTO ' + cls_pod.table_dict + ' (fid,key,value) VALUES (?,?,?)', (inst.id, attr, new_value,))                    
                
        self.mutables.clear()
                
        self.connection.commit()
    
        if clear_cache:
            self.cache.clear_cache()
        
        if close:
            self.connection.close()
            
    def cancel(self, clear_cache = True, close = False):
        
        self.mutables.clear()
            
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
    
    def get_table_list(self, report_collections = True):
        return [str(table[0]) for table in self.execute(query = 'select name from sqlite_master where type = ?', args = ('table',)) if ('pod_collection_' not in str(table[0]) or report_collections)]

    def execute(self, query, args = ()):
        return self.cursor.execute(query, args)
    
    def executemany(self, query, seq_of_args):
        return self.cursor.executemany(query, seq_of_args)
        
    """ execute on global table """
    def sql_create_base_tables(self):
        # This was moved to seperate function in order not to conflict with clear . . . 
        self.cursor.execute("CREATE TABLE IF NOT EXISTS pod_classes (id INTEGER PRIMARY KEY AUTOINCREMENT, cls_name TEXT UNIQUE, ctime INTEGER, mtime INTEGER, index_kv INTEGER, pod_types BINARY)")
        self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS cls_name_index ON pod_classes (cls_name)")
        

    

    """ execute on class table """
 
class Pickler(object):

    def __init__(self, db):
        self.db    = db
        self.cache = db.cache

    @staticmethod
    def persistent_id(value):
        return object.__getattribute__(value,'get_full_id')() if isinstance(value, (core.Object,core.NoSave)) else None
    
    class PersistentLoad(object):
        
        def __init__(self, cache):
            self.cache = cache
        
        def __call__(self, id):
            id = id.split(':')
            return self.cache.get_inst(cls_id = int(id[0]), inst_id = int(id[1]))
          
    @staticmethod
    def dump(value):
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
        self.undefineds   = {}

    def get_inst(self, cls_id, inst_id): 

        cls_pod = self.class_pods.get(cls_id, None)
        
        if cls_pod:
            return cls_pod.inst_get_inst_by_id(inst_id = inst_id, zombie = True)
        elif cls_id == 0 and inst_id == 0:
            return None
        else:
            id = (cls_id, inst_id)
            if id in self.undefineds:
                return self.undefineds[id]
            else:
                undefined = core.Undefined(id = (cls_id, inst_id), cache = self)
                self.undefineds[id] = undefined
                return undefined
            
    def clear_cache(self):            
        for cls_pod in self.class_pods.itervalues():
            cls_pod.clear()
        self.undefineds.clear()
    
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
            raise PodStoreError, "The key '" + key + "' was not found in the database store all . . . "

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __setitem__(self, key, value):
        self.db.execute(query = "INSERT OR REPLACE INTO pod_store_all (key_name,value) VALUES (?,?)", args = (self.prefix + key, self.db.pickler.dump(value),))
        
    def __setattr__(self, key, value):
        return self.__setitem__(key, value)     
