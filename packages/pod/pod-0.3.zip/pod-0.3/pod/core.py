import os
import sys
import time
import exceptions
import warnings
import inspect

import db
from column import Column, Int
from query  import Query, RawQuery
import fn

PY_VERSION_IS_25 = sys.version[0:3] == '2.5'

class PodMetaError(exceptions.BaseException):
    pass

class Meta(type):
    
    def __init__(cls, name, bases, dict):      
        
        if cls.__module__ == Meta.__module__:
            # We don't want to create tables and so on for the base classes defined in this module.
            return

        if len(bases) > 1:
            raise PodMetaError, "Currently, pod does not support multiple inheritance . . . "
                
        for key in ['id', 'pod', 'state']:
            if key in dict:
                raise PodMetaError, "'" + key + "' is a reserved class variable and cannot be defined in class " + str(cls)
              
        type.__setattr__(cls, 'pod', type(cls).Pod(cls = cls, parent = bases[0] if bases[0] is not Object else None))
               
    def __getattribute__(cls, key):
        
        if key in set(['__new__', '__instancecheck__', 'pod', '__class__', '__dict__']) or key in type.__getattribute__(cls, '__dict__'):
            return type.__getattribute__(cls, key)     
        elif key == 'store':
            store = db.Store(db = type.__getattribute__(cls, 'pod').db, prefix = type.__getattribute__(cls, 'pod').table + '_store_')
            type.__setattr__(cls, 'store', store)
            return store
        elif key == 'id':
            id = Int(index = False, cls_pod = type.__getattribute__(cls, 'pod'), name = 'id')
            type.__setattr__(cls, 'id', id)
            return id
        else:
            return type.__getattribute__(cls, key)
  
    def __setattr__(cls, key, value):
        
        # Here, __setattr__ is only performing error checking because dynamic creation of columns has been removed . . . 
        
        if key in set(['pod', 'id', 'store']):
            raise PodMetaError, "Key '" + key + "' is a reserved attribute of pod classes . . . "
        
        if isinstance(value, Column):
            raise PodMetaError, "You cannot create a column '" + key + "' dynamically -- please add it to the class header . . . "
        
        if isinstance(getattr(cls, key, None), Column):
            raise PodMetaError, "Attr '" + key + "' is of type pod.Column -- you cannot alter this attribute dynamically -- it must be performed in class header . . ."
        
        return type.__setattr__(cls, key, value)
        
    def __iter__(cls):
        return Query(where = cls)
            
    def execute(cls, query, args = ()):
        return cls.pod.cursor.execute(query.replace("cls_table", cls.pod.table).replace("cls_dict_table", cls.pod.table_dict), args)

    def executemany(cls, query, args = ()):
        return cls.pod.cursor.executemany(query.replace("cls_table", cls.pod.table).replace("cls_dict_table", cls.pod.table_dict), args)
        
    def migrate(cls, new_cls):
        cls.pod.schema_migrate_to_new_cls(new_cls = new_cls)
        
    def drop(cls):
        cls.pod.table_drop()
    
    def clear(cls):
        cls.pod.table_clear()
        
    def get_count(cls, child_classes = True, count = 0):
        get_one = RawQuery(select = fn.count(cls.id) >> 'count').get_one()

        count = get_one.count + count if get_one else count
        
        if child_classes:
            for child_pod in cls.pod.child_pods:
                count = child_pod.cls.get_count(child_classes = child_classes, count = count)
        return count
        
    def get_db(self):
        return type.__getattribute__(cls, 'pod')
    
    class Pod(object):
    
        def __init__(self, cls, parent):
            # pass ins
            self.cls            = cls
            self.parent_pod     = getattr(parent, 'pod', None)
            self.db             = None
            
            self.table      = self.get_table_name()
            # register table name 
            register.class_pods[self.table] = self
        
            # Init vars
            self.column_group            = {}
            self.column_callbacks_create = set()
            self.column_callbacks_load   = set()
            self.child_pods              = set()  
            
            # First, update parent and add any columns a parent has to your local dictionary. 
            # The reason you need a local copy of a column is because if you have a ParentClass, ChildClass and a column called 'name'
            # you want ParentClass.name == 'Fred' to return all objects with a name of 'Fred' but ChildClass.name == 'Fred' to 
            # only return ChildClass object with a name == 'Fred'.  column_add_parents takes care of this . . .

            # This updates all the columns passed in from the class header. 
            for name,column in self.cls.__dict__.iteritems():
                 if isinstance(column, Column):
                    self.column_group[name] = column
                    column.update(cls_pod = self, name = name)


            if self.parent_pod is not None:
                object.__getattribute__(self.parent_pod, 'child_pods').add(self)
                for name,column in object.__getattribute__(self.parent_pod, 'column_group').iteritems():
                    if name in self.cls.__dict__:
                        raise PodMetaError, "Class " + str(self.cls) + " is trying to add column " + name + ", but this column already defined in parent " + str(object.__getattribute__(self.parent_pod, 'cls')) + " . . ."
                    else:
                        column = column.get_deep_copy(cls_pod = self, name = name)
                        type.__setattr__(self.cls, name, column)
                        self.column_group[name] = column
                        
                
                
            self.__class__ = type.__getattribute__(self.cls, 'PodZombie')
            
        def __getstate__(self):
            raise PodMetaError, "You cannot pickle a Pod CLASS pod._Meta object . . . "
        
        def activate(self, row = None):
        
            self.set_db()
                          
            self.table_dict = self.table + '_kvdict'
            
            if row is None: 
                row = self.cursor.execute("SELECT id,mtime FROM pod_classes WHERE cls_name=(?)", (self.table,)).fetchone()
                    
                if row is None:   
                    self.id              = None
                    self.inst_new_backup = self.inst_new
                    self.inst_new        = self.table_create
                    return
    
                self.id = int(row[0])    
            else:
                self.id    = int(row[0])
                self.mtime = row[1]
            
            self.mtime = self.get_mtime(source_file = inspect.getsourcefile(self.cls))

            self.activate_on_set_id()
                    
            if int(row[1]) != self.mtime:
                self.column_check_for_changes()
                
        def activate_on_set_id(self):
            # This is used by both activate and table_create
            self.db.cache.class_pods[self.id] = self
            self.cache                        = {}      
            for column in self.column_group.itervalues():
                column.on_activate()
     
        def set_db(self):
            #
            # This hierarchically searches for the correct database. If: 
            # 1.  The database is already set, return it. 
            # 2.  If the database was constructed without the 'attach' parameter, the global database is used
            # 3.  Else, search the parent hierarchy for a valid database name 
            #
            # Also, set the cursor
            #
            if self.db is None:
                if self.db is None and db.current.global_db:
                    self.db = db.current.global_db
                else:
                    self.db = self.parent_pod.set_db() if self.parent_pod else None                  
                if self.db is None:
                    raise PodMetaError, "You have not connected " + str(self.cls) + " to any databases and " + str(self.cls) + " needs to be activated . . . "
            if self.db:
                self.cursor  = self.db.cursor
                self.pickler = self.db.pickler
            
            # This checks to see if there are any 'conflicts' between your db and your parents database . . . 
            if self.parent_pod:
                parent_pod_db = object.__getattribute__(self.parent_pod, 'db')                
                if parent_pod_db and parent_pod_db is not self.db:
                    raise PodMetaError, "The class " + str(self.cls) + " descends from " + str(self.parent_pod.cls) + " but is connected to a different database . . . "            
            return self.db 
                        
        def get_table_name(self):
            #
            # The table name is: 
            #   1. The module path plus the class name, for example myapp_models_Person. 
            #   2. Just the class name (e.g. just Person) if the user has set POD_TABLE_NAME set to True
            #      in class header. 
            #   3. POD_TABLE_NAME if it's set to a string in the class header
            #
            #   Full name is harder to read if working with sql table directly, but 
            #   uses full module name so it is less likely to have a namespace collision. 
            #
            cls_name       = type.__getattribute__(self.cls, '__name__')
            pod_table_name = type.__getattribute__(self.cls, '__dict__').get('POD_TABLE_NAME', None)
            if pod_table_name is None:
                return '_'.join(self.cls.__module__.split('.') + [cls_name])
            elif pod_table_name is True:
                return cls_name
            else:
                return pod_table_name
        
        def get_mtime(self, source_file = None):
            return int(os.path.getmtime(source_file)) if source_file else int(time.time())
           
        """ TABLE OPERATIONS """
        def table_create(self, inst = None, kwargs = None, create_inst = True):
            
            self.mtime = self.get_mtime(source_file = inspect.getsourcefile(self.cls))

            # if row is None, means a new class and a new table needs to be made  
            self.cursor.execute("INSERT INTO pod_classes (cls_name, ctime, mtime) VALUES (?,?,?)", (self.table,self.mtime,self.mtime,))
            self.id = self.cursor.lastrowid
            self.cursor.execute("CREATE TABLE IF NOT EXISTS " + self.table + " (id INTEGER PRIMARY KEY AUTOINCREMENT)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS " + self.table_dict + " (fid INTEGER, key TEXT, value BINARY, PRIMARY KEY (fid, key))")

            self.activate_on_set_id()
                        
            for name,column in self.column_group.iteritems():
                self.column_create(name = name, column = column, is_new = True)
            
            if len(self.column_group) == 0:
                self.column_commit_to_db()
                                                             
            self.inst_new = self.inst_new_backup
            del self.inst_new_backup
            return self.inst_new(inst = inst, kwargs = kwargs) if create_inst else None
                       
        def table_drop(self):
            if self.id:
                self.cursor.execute("DELETE FROM pod_classes WHERE id=?", (self.id,))
                self.cursor.execute("DROP TABLE IF EXISTS " + self.table)                    
                self.cursor.execute("DROP TABLE IF EXISTS " + self.table_dict)                    
                self.db.commit(clear_cache = True, close = True)
                for child_pod in self.child_pods:
                    child_pod.table_drop()

        def table_clear(self, child_classes = True):
            if self.id:                     
                self.cache.clear()            
                self.cursor.execute("DELETE FROM " + self.table)                    
                self.cursor.execute("DELETE FROM " + self.table_dict)                    
                if child_classes:
                    for child_pod in self.child_pods:
                        child_pod.table_clear()

        """ COLUMN OPERATIONS """
        def column_print_msg(self, msg = None):
            
            if self.db.chatty:
                if 'start_message' not in self.__dict__:
                    self.start_message = "Class '" + self.cls.__name__ + "' needs to be created/updated . . . checking to see if any columns need to be updated:"
                if self.start_message:
                    print self.start_message
                    self.start_message = False
                if msg:
                    print "\tFor class '" + self.cls.__name__ + "' " + msg
            
        def column_check_for_changes(self, copy_dropped_to_dict = True):
            
            if self.db.chatty:
                self.column_print_msg(msg = None)

            old_columns = self.db.pickler.load(self.cursor.execute("SELECT columns FROM pod_classes WHERE id=(?)", (self.id,)).fetchone()[0])
            set_old_columns = set(old_columns.keys())
            
            for name,col in old_columns.iteritems():
                col.update(cls_pod = self, name = name)
            
            if set(self.column_get_current_db_columns()) != set_old_columns:
                raise PodMetaError, "Fatal error -- columns in table are not same as columns in class table . . ."
            
            # All the things that could change: 
            #
            #    What could happen:
            #         1. Drop:         the new_columns might not have a column found in old_columns -->  In this case, drop the old column. 
            #         2. Add:          the new_columns might have a column not found in old_columns -->  In this case, add the new column. 
            #         3. Change Type:  a new_column might have changed type -- in this case, drop and add. 
            #         4. Change Index: the new_columns might have a column whose index is not the same as the old column --> In this case, either add/drop index on that column. 
            #         5. Do nothing!:  a new column and the old column match!!!  YES!!
            #
            #    After this, update the mtime on the class and restore column in the database. 

            set_new_columns = set(self.column_group.keys())
            
            set_changed_type_columns = set([name for name in set_new_columns & set_old_columns if self.column_group[name].__class__ != old_columns[name].__class__])
            
            # You need to drop 1) all columns that changed type and 2) if auto_drop is true, you need to also drop set_old_columns - set_new_columns
            #
            # ** auto_drop no longer supported, so this line has changed
            # set_drop_columns = set_changed_type_columns if self.auto_drop is False else set_changed_type_columns | (set_old_columns - set_new_columns)
            set_drop_columns = set_changed_type_columns | (set_old_columns - set_new_columns)
            set_add_columns = set_changed_type_columns | (set_new_columns - set_old_columns)
                       
            # 1. Drop 
            if len(set_drop_columns) > 0:
                self.column_drop_old(old_columns = old_columns, set_old_columns = set_old_columns, set_drop_columns = set_drop_columns, copy_dropped_to_dict = copy_dropped_to_dict)

            # 2. Add
            for name in set_add_columns:
                self.column_create(name = name, column = self.column_group[name], is_new = False)

            # 4. Change index
            for new_column, old_column in [(self.column_group[name], old_columns[name]) for name in (set_old_columns & set_new_columns)]:   
                if new_column.index is True and old_column.index is False:
                    self.column_add_index(name = name)
                elif new_column.index is False and old_column.index is True:
                    self.column_drop_index(name = name)
                    
            self.column_commit_to_db()
            
        def column_drop_old(self, old_columns, set_old_columns, set_drop_columns, copy_dropped_to_dict):
            
            set_keep_columns = set_old_columns - set_drop_columns
            self.column_print_msg(msg = "dropping columns " + ",".join(set_drop_columns) + "  . . . ")
            list_keep_columns = list(set_keep_columns)
            list_drop_columns = list(set_drop_columns)

            if copy_dropped_to_dict and len(list_drop_columns) > 0:
                self.cursor.execute("SELECT " + ",".join(['id'] + list_drop_columns) + " FROM " + self.table)
                args = []
                for row in self.cursor.fetchall():
                    for i,col_name in enumerate(list_drop_columns):
                        args.append((row[0], col_name, self.db.pickler.dump(old_columns[col_name].load(row[i+1]))))
                self.cursor.executemany("INSERT OR REPLACE INTO " + self.table_dict + " (fid,key,value) VALUES (?,?,?)", args)

                        
            # Now, put humpty dumpty back together again . . . 
            self.cursor.execute("SELECT " + ",".join(['id'] + list_keep_columns) + " FROM " + self.table)
            rows = self.cursor.fetchall()
                        
            self.cursor.execute("DROP TABLE IF EXISTS " + self.table)                
            self.cursor.execute("CREATE TABLE IF NOT EXISTS " + self.table + " (id INTEGER PRIMARY KEY)")
            
            for name in list_keep_columns:
                old_columns[name].update(cls_pod = self, name = name)
                self.column_create(name = name, column = old_columns[name], is_new = True)
            
            # NOW PUT ALL THE ROWS BACK INTO DB -- HOWEVER, COPY PED COLUMN DATA BACK INTO THE DICT

            names  = '(' + ",".join(['id'] + list_keep_columns) + ')'                
            quest  = '(' + ",".join(["?" for i in range(len(list_keep_columns)+1)]) + ')'
            self.cursor.executemany("INSERT INTO " + self.table + " " + names + " VALUES " + quest, (row[0:len(list_keep_columns)+1] for row in rows))
                
        def column_drop_and_delete_forever(self, column):

            if self.db.chatty:
                print "You have chosen to permentally drop and delete column '" + column.name + "' from '" + self.table + "'.  All data will be lost forever "
                print "Remember!  You have to remove this column from the class header or else it will be added back on next import . . . "
            
            delattr(self.cls, column.name)
            del self.column_group[column.name]
            
            self.column_check_for_changes(copy_dropped_to_dict = False)
            
            for child_pod in self.child_pods:
                child_pod.column_drop_and_delete_forever(child_pod.column_group[column.name])

            # Now you want to resave a local mtime, because we want to reimport the class after this . . . 
            self.column_commit_to_db(mtime = self.get_mtime())
            
        def column_create(self, name, column, is_new):
            # If the column is new, then you don't need to copy all the data from the __dict__ to the new column. 
                    
            self.column_print_msg(msg = "adding column '" + name + "'  . . . ")
            self.cursor.execute("ALTER TABLE " + self.table + " ADD COLUMN " + column.get_alter_table())
    
            if column.index:
                self.column_add_index(name = name)
                
            if is_new is False:
                # IF NOT NEW, THEN, ADD COLUMN TO DATABASE
                self.cursor.execute("SELECT fid,value FROM " + self.table_dict + " WHERE key=?", (name,))                          
                # NOW, COPY THE NEW VALUE FROM THE inst.__dict__ TO THE COLUMN . . . 
                self.cursor.executemany("UPDATE " + self.table + " SET " + name + "=? WHERE id=?", [(column.dump(self.db.pickler.load(row[1])), row[0]) for row in self.cursor.fetchall()])
                self.cursor.execute("DELETE FROM " + self.table_dict + " WHERE key=?", (name,))
                                    
            # And finally, store new columns to database 
            self.column_commit_to_db()       
        
        def column_add_index(self, name):
            self.column_print_msg(msg = "adding index '" + name + "'  . . . ")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS " + self.table + "_pin_" + name + " ON " + self.table + " (" + name +")")
                    
        def column_drop_index(self, name):        
            self.column_print_msg(msg = "dropping index '" + name + "'  . . . ")
            self.cursor.execute("DROP INDEX IF EXISTS " + self.table + "_pin_" + name)
                   
        def column_get_current_db_columns(self):            
            self.cursor.execute("PRAGMA table_info(" + self.table + ")")
            return [str(col[1]) for col in self.cursor.fetchall() if str(col[1]) != 'id']
        
        def column_get_current_db_indexes(self):
            self.cursor.execute("PRAGMA index_list(" + self.table + ")")
            return [str(col[1]).replace(self.table + "_pin_", "") for col in self.cursor.fetchall()]
                 
        def column_commit_to_db(self, mtime = None):
            mtime = self.mtime if mtime is None else mtime
            self.cursor.execute("UPDATE pod_classes SET mtime=?,columns=? WHERE id=?", (mtime,self.db.pickler.dump(self.column_group),self.id,))      
            self.db.connection.commit()
                                  
        """ instance methods """
        def inst_new(self, inst = None, kwargs = None):

            if inst is None:
                inst = self.cls.__new__(self.cls)       
                
            # This is for special column types (like column.TimeCreate) which want to do something on create . . 
            for col in set(self.column_callbacks_create) | set(self.column_callbacks_load):
                inst,kwargs = col.on_inst_create(inst = inst, kwargs = kwargs)
                   
            col_names  = "("
            col_quest  = "("
            col_values = []
            nom_values = []
           
            if kwargs is not None:
                for key,value in kwargs.iteritems():
                    self.__setattr__(key,value)
                    if key in self.column_group:
                        col_names += key + ','
                        col_quest += '?,'
                        col_values.append(self.column_group[key].dump(value))
                    else:
                        nom_values.append([None,key,self.pickler.dump(value),])
    
            if len(col_values) == 0:
                if PY_VERSION_IS_25 or True:
                    # There is a bug in the sqlite3 bindings in 2.5.4
                    self.cursor.execute("INSERT INTO " + str(self.table) + " (id) VALUES (NULL)")
                else:
                    self.cursor.execute("INSERT INTO " + str(self.table) + " DEFAULT VALUES")
            else:
                self.cursor.execute('INSERT INTO ' + self.table + ' ' + col_names[:-1] + ') VALUES ' + col_quest[:-1] + ')', col_values)

            inst_id = self.cursor.lastrowid
     
            if len(nom_values) > 0:
                for value in nom_values:
                    value[0] = inst_id
                self.cursor.executemany('INSERT INTO ' + self.table_dict + ' (fid,key,value) VALUES (?,?,?)', nom_values)                    

            object.__setattr__(inst, 'id', inst_id)
            object.__setattr__(inst, '_pod_exists', True)
                                  
            self.cache[inst_id] = inst
                                        
            object.__getattribute__(inst, 'on_new_or_load_from_db')()
            return inst
                  
        def inst_get_inst_by_id(self, inst_id, exists = None):
            
            if inst_id in self.cache:
                return self.cache[inst_id]                
            else:
                inst = self.cls.__new__(self.cls)
                object.__setattr__(inst, 'id', inst_id)
                object.__setattr__(inst, '_pod_exists', exists)
                object.__getattribute__(inst, 'on_new_or_load_from_db')()
                object.__getattribute__(inst, 'on_load_from_db')()
                self.cache[inst_id] = inst
                for col in self.column_callbacks_load:
                    inst = col.on_inst_load(inst = inst)
                return inst
        
        def inst_update_dict(self, inst, kwargs):
            object.__getattribute__(inst, '__dict__').update(kwargs)
            col_attrs  = ""
            col_values = []
            nom_values = []
            id         = inst.id         
               
            for key,value in kwargs.items():
                self.__setattr__(key,value)
                if key in self.column_group:
                    col_attrs += key + '=?,'
                    col_values.append(self.column_group[key].dump(value))
                else:
                    nom_values.append((id,key,self.pickler.dump(value),))

            if len(col_values) > 0:
                col_values.append(id)
                self.cursor.execute('UPDATE ' + self.table + ' SET ' + col_attrs[:-1] + ' WHERE id=?', col_values)
 
            if len(nom_values) > 0:
                self.cursor.executemany('INSERT OR REPLACE INTO ' + self.table_dict + ' (fid,key,value) VALUES (?,?,?)', nom_values)                    
                      
        def inst_load_attr_from_db(self, inst, attr):
            
            if attr in self.column_group:
                self.cursor.execute("SELECT " + attr + " FROM " + self.table + " WHERE id=?",(object.__getattribute__(inst,'id'),))
                row = self.cursor.fetchone()
                if row:
                    object.__setattr__(inst, '_pod_exists', True)
                    object.__setattr__(inst, attr, self.column_group[attr].load(row[0]))                    
                else:
                    raise PodObjectDeleted, "The object " + str(inst) + " with id " + inst.get_full_id() + " had been deleted . .  ."
            else:
                self.cursor.execute("SELECT value FROM " + self.table_dict + " WHERE fid=? AND key=?",(object.__getattribute__(inst,'id'),attr,))
                row = self.cursor.fetchone()
                if row:
                    object.__setattr__(inst, '_pod_exists', True)
                    object.__setattr__(inst, attr, self.db.pickler.load(row[0]))
                else:
                    # Now, you need to check for existence
                    if self.inst_check_if_exists(inst) is False:
                        raise PodObjectDeleted, "The object " + str(inst.inst) + " with id " + inst.get_full_id() + " has been deleted . .  ."

        def inst_set_attr(self, inst, attr, value):
            if attr in ['__class__', 'id', '_pod_exists']:
                raise PodObjectError, "You cannot set attr '" + attr + "' of a pod object . . ."
            if self.inst_check_if_exists(inst):
                object.__setattr__(inst, attr, value)              
                if attr in self.column_group:
                    self.cursor.execute('UPDATE ' + self.table + ' SET ' + attr + '=? WHERE id=?', (self.column_group[attr].dump(value),inst.id,))
                else:
                    self.cursor.execute('INSERT OR REPLACE INTO ' + self.table_dict + ' (fid,key,value) VALUES (?,?,?)', (inst.id,attr,self.pickler.dump(value),))                    
            else:
                raise PodObjectDeleted, "You tried to set an attributed on a deleted pod object '" + inst.get_full_id() + "' . . . "
        
        def inst_del_attr(self, inst, attr):
            # If the attribute is in inst's columns, you can't really delete it -- just set it to None (since the column will have NULL)
            # If not in column group, then delete it from the table. 
            id = object.__getattribute__(inst,'id')
            if attr in self.column_group:
                self.cursor.execute('UPDATE ' + self.table + ' SET ' + attr + '=NULL WHERE id=?', (id,))
                return None
            else:
                self.cursor.execute("DELETE FROM " + self.table_dict + " WHERE fid=? AND key=?", (id,attr,))
                return object.__delattr__(inst, attr)
                      
        def inst_delete(self, inst):
            object.__getattribute__(inst, 'pre_delete')()
            id = object.__getattribute__(inst,'id')
            self.cursor.execute("DELETE FROM " + self.table      + " WHERE id=?",  (id,))
            self.cursor.execute("DELETE FROM " + self.table_dict + " WHERE fid=?", (id,))
            if id in self.cache:
                del self.cache[id]
            # THEN, MAKE IT A DELETED OBJECT()
            object.__setattr__(inst, '__class__', Deleted)
            object.__setattr__(inst, '__dict__',  {})
            return None

        def inst_full_load(self, inst):                    
            cursor   = self.cursor
            id       = object.__getattribute__(inst,'id')
            cols     = [col for col in self.column_group.keys()]
            load     = self.db.pickler.load        
            cursor.execute("SELECT " + ",".join(['id'] + cols) + " FROM " + self.table + " WHERE id=?",(id,))
            row = cursor.fetchone()
            if row:
                object.__setattr__(inst, '_pod_exists', True)
                for i,name in enumerate(cols):
                    object.__setattr__(inst, name, self.column_group[name].load(row[i+1]))
                cursor.execute("SELECT key,value FROM " + self.table_dict + " WHERE fid=?",(id,))
                rows = cursor.fetchall()
                for kv in rows:
                    object.__setattr__(inst, kv[0], load(kv[1]))               
            else:
                raise PodObjectDeleted, "The object " + str(inst) + " with id " + inst.get_full_id() + " had been deleted . .  ."
          
        def inst_check_if_exists(self, inst):
            pod_exists = object.__getattribute__(inst, '_pod_exists')
            if pod_exists is None:
                self.cursor.execute("SELECT id FROM " + self.table + " WHERE id=?",(object.__getattribute__(inst,'id'),))
                row = self.cursor.fetchone()
                if row:
                    object.__setattr__(inst, '_pod_exists', True)
                    return True
                else:
                    object.__setattr__(inst, '_pod_exists', False)
                    return False
            else:
                return pod_exists
        
        """ alter commands """        
        def schema_migrate_to_new_cls(self, new_cls):
            if new_cls.__bases__[0] is not object:
                raise PodMetaError, "The new_cls '" + new_cls.__name__ + "' must descend directly from object (you can change it later to pod.Object, but first migrate the old class over . . . "
            new_cls_name = self.get_table_name(db = self.db, cls = new_cls, cls_name = new_cls.__name__)
            self.cursor.execute("UPDATE pod_classes SET cls_name=? WHERE id=?", (new_cls_name, self.id,))
            self.cursor.execute("ALTER TABLE " + self.table      + " RENAME TO " + new_cls_name)
            self.cursor.execute("ALTER TABLE " + self.table_dict + " RENAME TO " + new_cls_name + '_kvdict')            
            self.db.commit(clear_cache = True, close = True)
              
    class PodZombie(object):
        
        def __setattr__(self, attr, vaule):
            raise PodMetaError, "You cannot set an attribute on this object . . . "
        
        def __getattribute__(self, attr):
            object.__setattr__(self, '__class__', type.__getattribute__(object.__getattribute__(self, 'cls'), 'Pod'))
            self.activate()
            return self.__getattribute__(attr)

class register:
    class_pods    = {}
              
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
##
##   Object: THE OBJECT IN P'O'D
##
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class PodObjectError(exceptions.BaseException):
    pass

class PodObjectDeleted(exceptions.BaseException):
    pass

class PodObjectUndefined(exceptions.BaseException):
    pass

class Object(object):

    __metaclass__ = Meta
                
    def __init__(self, **kwargs):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_new(inst = self, kwargs = kwargs)

    def __reduce__(self):
        return handle_unreduce, (object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').id, object.__getattribute__(self, 'id'))
        
    def __getattribute__(self, attr):  
        
        dict = object.__getattribute__(self, '__dict__')
        
        if attr in dict:
            value = dict[attr]
        elif attr == '__dict__':
            return dict
        else:
            cls_pod = object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod')            
            if attr in cls_pod.column_group:
                cls_pod.inst_load_attr_from_db(self, attr)
                value = dict[attr]
            else:
                return object.__getattribute__(self, attr)  # This, then, will call __getattr__ on fail and try to load from database . . . 

        if value is not None and not isinstance(value, (Object, NoSave, str, int, float, bool, long, complex, tuple, frozenset)):
            object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').db.dirty[(self, attr)] = value
        
        return value
                  
    def __getattr__(self, attr):
        dict = object.__getattribute__(self, '__dict__')
        cls_pod = object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod')            
        cls_pod.inst_load_attr_from_db(self, attr)
        if attr in dict:
            value = dict[attr]
            if value is not None and not isinstance(value, (Object, NoSave, str, int, float, bool, long, complex, tuple, frozenset)):
                object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').db.dirty[(self, attr)] = value
            return value
        else:
            raise AttributeError, "'" + self.__class__.__name__ + "' object has no attribute '" + attr + "'"
                            
    def __setattr__(self, attr, value):   
        return object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_set_attr(self, attr, value)
    
    def __delattr__(self, attr):
        return object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_del_attr(self, attr)
        
    def delete(self):
        return object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_delete(self)
    
    def full_load(self):
        return object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_full_load(self)
        
    def get_full_id(self):
        return str(object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').id) + ":" + str(object.__getattribute__(self, 'id')) 

    def set_many(self, **kwargs):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_update_dict(self, kwargs)

    def update(self, other):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_update_dict(self, other)

    """ pass through convenience functions """
    def on_new_or_load_from_db(self):
        pass

    def on_load_from_db(self):
        pass
        
    def pre_save(self):
        pass
    
    def pre_cancel(self):
        pass
    
    def pre_delete(self):
        pass
               
class NoSave(object):
    
    def __reduce__(self):
        return handle_nosave, ()
  
class Deleted(NoSave):
    
    def __getattr__(self, key):
        raise PodObjectUndefined, "You tried to get attr '" + key + "' on a pod.Deleted object -- this means that this is a reference to an object that was deleted . . . "
    
    def __setattr__(self, key, value):
        raise PodObjectUndefined, "You tried to set attr '" + key + "' on a pod.Deleted object -- this means that this is a reference to an object that was deleted . . . "

class Undefined(NoSave):
    
    def __init__(self, id, cursor):
        object.__setattr__(self, 'id',     id)
        object.__setattr__(self, 'cursor', cursor)
        
    def __reduce__(self):
        return handle_unreduce, object.__getattribute__(self, 'id')
    
    def __reduce_ex__(self, protocol_version):
        return handle_unreduce, object.__getattribute__(self, 'id')
        
    def get_full_id(self):
        return str(self.id[0]) + ":" + str(self.id[1])

    def __getattribute__(self, key):
        if key in ['__init__', '__reduce__', '__reduce_ex__', 'get_full_id']:
            return object.__getattribute__(self, key)
        else:
            object.__getattribute__(self, 'try_to_activate_class')('get', key)
            # The above function changes the class, preventing an infinite loop
            return self.__getattribute__(key)

    def __setattr__(self, key, value):
        object.__getattribute__(self, 'try_to_activate_class')('set', key)
        raise PodObjectUndefined, "You tried to set attr '" + key + "' on a pod.Undefined object -- this means the class was not loaded at import time . . . "
    
    def try_to_activate_class(self, type, key):
        id  = object.__getattribute__(self, 'id')
        row = object.__getattribute__(self, 'cursor').execute("SELECT cls_name,mtime FROM pod_classes WHERE id=(?)", (id[0],)).fetchone()                
        cls_name,mtime = row[0],row[1]
        if cls_name in register.class_pods:
            cls_pod = register.class_pods[cls_name]
            cls_pod.activate(row = [id[0], mtime])
            object.__setattr__(self, '__class__',          cls_pod.cls)
            object.__setattr__(self, 'id',                 id[1])
            object.__setattr__(self, '_pod_exists',        True)
            object.__delattr__(self, 'cursor')
        else:
            raise PodObjectUndefined, "You tried to " + type + " attr '" + key + "' on a pod.Undefined of class type '" + cls_name + "' -- this means the class was not loaded at import time. . . "
        
""" These methods handle unpickling """
def handle_unreduce(*args):
    return db.current.cache.get_inst(cls_id = args[0], inst_id = args[1])

def handle_nosave(*args):
    return None


