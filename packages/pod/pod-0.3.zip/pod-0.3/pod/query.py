import exceptions
import sqlite3

import core

""" ############################################################################################
###
###    THE QUERY 
###
""" ############################################################################################
    
class PodQueryError(exceptions.BaseException):
    pass
                
class Query(object):

    def __init__(self, select = None, where = None, order_by = None, offset = None, limit = None, get_children = True):

        self.select        = select
        self.where         = where
        self.order_by      = order_by
        self.limit         = limit
        self.offset        = offset
        # Other flags . . . 
        self.get_children  = get_children
        self.db            = None
        self.active        = False
    
    def __iter__(self):
        return self
        
    def get_sql_setup(self):
        
        if isinstance(self.where, core.Meta):
            cls_pod = type.__getattribute__(self.where, 'pod')
            where = None
        elif self.where:
            self.where.get_sql(full_name = False, type = 'where')
            if len(self.where.class_pods) > 1:
                raise PodQueryError, "You cannot mix class types in a pod.Query where statement -- use pod.RawQuery instead . . . "
            cls_pod = self.where.class_pods.pop()
            where = self.where
        else:
            raise PodQueryError, "Improper where statement . . ."

        self.db              = cls_pod.db
        self.class_pod_list  = self.get_class_list(cls_pod = cls_pod, list = [])
        
        return cls_pod,where
        
    def get_sql(self):

        if self.select:
            self.select.get_sql(full_name = False)
            if len(self.select.class_pods) > 1:
                raise PodQueryError, "You cannot mix class types in a pod.Query select statement -- use pod.RawQuery instead . . . "
        
        if self.where is None:
            self.where = [class_pod for class_pod in self.select.class_pods][0].cls
        
        cls_pod,where = self.get_sql_setup()
                    
        if self.order_by:
            self.order_by.get_sql(full_name = False)

        sql,values = "",[]

        for i,cls_pod in enumerate(self.class_pod_list):
                        
            if i > 0:
                sql += " UNION " 

            sql += "SELECT " + str(i) + " AS PODCLASS,id"
            
            if self.select:
                sql    += "," + self.select.expression 
                if len(self.select.args) > 0:
                    raise PodQueryError, "You cannot do any processing within a pod.Query select statement -- use pod.RawQuery instead . . . "
                values += self.select.args
                
            sql += " FROM " + cls_pod.table
            
            if where:
                sql    += " WHERE " + where.expression
                values += where.args
            
        if self.order_by is not None:
            sql += " ORDER BY " + self.order_by.expression
                
        if self.limit is not None:
            sql += " LIMIT " + str(self.limit)

        if self.offset is not None:
            sql += " OFFSET " + str(self.offset)

        return sql,values
            
    def get_class_list(self, cls_pod, list):
        
        if cls_pod.id is not None:
            list.append(cls_pod)
        
        if self.get_children:
            for new_cls_pod in cls_pod.child_pods:
                list = self.get_class_list(cls_pod = new_cls_pod, list = list)
            
        return list
     
    """
    The meat of the iterator
    """
    def next(self):
        if self.active is False:
            self.active = True
            sql,values = self.get_sql()  
            
            self.db.connection.row_factory = None
            
            if self.db.very_chatty:
                self.current_cursor = self.db.get_new_cursor()
            else:
                self.current_cursor = self.db.connection.cursor()
                    
            self.current_cursor.execute(sql, values)
            if self.current_cursor.description:
                columns = [desc[0] for desc in self.current_cursor.description][2:]
                if len(columns) > 0:
                    self.returned_columns = []
                    for i,cls_pod in enumerate(self.class_pod_list):
                        self.returned_columns.append([])
                        for j,col in enumerate(columns):
                            if col in cls_pod.column_group:
                                self.returned_columns[i].append((j+2,col, cls_pod.column_group[col]))   # Duck typing: both columns and pickler support 'load' method
                            else:
                                # This is where we check that the columns are right!
                                raise PodQueryError, "You asked for column '" + col + "' but it is not a defined pod.column . . . "
                else:
                    self.returned_columns = None
            return self.next()
        else:
            row     = self.current_cursor.next()
            cls_num = row[0]
            cls_pod = self.class_pod_list[cls_num]
            inst    = cls_pod.inst_get_inst_by_id(inst_id = row[1], exists = True)
            if self.returned_columns:
                new_results = {}
                for j,col,loader in self.returned_columns[cls_num]:
                    new_results[col] = loader.load(row[j])
                object.__getattribute__(inst, '__dict__').update(new_results)
            return inst

    """ 
    API
    """
    def get_one(self, error_on_multiple = True):
        objects = [object for object in self]
        if len(objects) == 0:
            return None
        else:
            if error_on_multiple and len(objects) > 1:
                raise PodQueryError, "More than one object returned . . . "
            return objects[0]
            
    def delete(self):
        cls_pod,where = self.get_sql_setup()
        
        for i,cls_pod in enumerate(self.class_pod_list):
            if where:
                ids    = [(row[0],) for row in cls_pod.cursor.execute('SELECT id FROM ' + cls_pod.table + ' WHERE ' + where.expression, where.args)]
                cls_pod.cursor.execute("DELETE FROM " + cls_pod.table + " WHERE " + where.expression, where.args)
                cls_pod.cursor.executemany("DELETE FROM " + cls_pod.table_dict + " WHERE fid=?", ids)
                
            

    """ If you want to reset a query . . . """
    def reset(self):
        self.active = False
                                            
class RawQuery(object):
    
    def __init__(self, select = None, distinct = False, where = None, order_by = None, group_by = None, having = None, offset = None, limit = None, cls = None):
    
        self.select   = select
        self.distinct = distinct
        self.where    = where
        self.order_by = order_by
        self.group_by = group_by
        self.having   = having 
        self.offset   = offset
        self.limit    = limit
        Row.cls       = Row if cls is None else cls

        self.db            = None
        self.active        = False
        
    def __iter__(self):
        return self
    
    def get_sql(self):
        
        if isinstance(self.where, core.Meta):
            class_pods = set(self.where)
            where   = None
            self.db = class_pods[0].db
        elif self.where:
            where = self.where
            where.get_sql(full_name = False, type = 'where')
            self.db = None
            class_pods = self.where.class_pods
        else:
            class_pods = set()
        
        sql,values = "",[]    
        
        sql += "SELECT "
        
        if self.distinct:
            sql += "DISTINCT "
        
        if self.select:
            self.select.get_sql(full_name = True, type = 'select')
            sql        += self.select.expression            
            values     += self.select.args
            class_pods |= self.select.class_pods
        else:
            sql += "* "
        
                    
        sql += " FROM " + ",".join([cls_pod.table for cls_pod in class_pods])

        if self.where:
            self.where.get_sql(full_name = True)
            sql    += " WHERE " + where.expression
            values += where.args
    
        if self.group_by:
            self.group_by.get_sql(full_name = True, type = 'group_by')
            sql    += " GROUP BY " + self.group_by.expression            
            values += self.group_by.args
        
        if self.having:
            self.having.get_sql(full_name = True, type = 'where')
            sql    += " HAVING " + self.having.expression            
            values += self.having.args
    
        if self.order_by:
            self.order_by.get_sql(full_name = True)
            sql += " ORDER BY " + self.order_by.expression
                
        if self.limit:
            sql += " LIMIT " + str(self.limit)
    
        if self.offset:
            sql += " OFFSET " + str(self.offset)

        # Now, define a database connection
        for cls_pod in class_pods:
            if self.db is None:
                self.db = cls_pod.db
            elif self.db is not cls_pod.db:
                raise PodQueryError, "You are trying to get records from classes from different database connections . . . "

        # This checks to see if any of the tables have yet to be created. 
        # If they haven't, return an empty query
        for cls_pod in class_pods:        
            if cls_pod.id is None:
                return '',() 
        return sql,values        
    
    def next(self):
        if self.active is False:
            # First, activate make sure the Row.cls has a table if it's a pod.Object
            # If you don't do this, you'll get this error: sqlite3.OperationalError: cannot commit transaction - SQL statements in progress
            if isinstance(Row.cls, core.Meta) and Row.cls.pod.id is None:
                print Row.cls.pod.table_create(inst = None, kwargs = None, create_inst = False)
                
            self.active = True
            sql,values = self.get_sql()  
            self.db.connection.row_factory = Row
            if self.db.very_chatty:
                self.current_cursor = self.db.get_new_cursor()
            else:
                self.current_cursor = self.db.connection.cursor()
            self.current_cursor.execute(sql, values)
            
            # Now, setup the row factory . .  .    
            if self.current_cursor.description:        
                Row.columns = [desc[0].split(".")[-1] for desc in self.current_cursor.description]
            if isinstance(Row.cls, core.Meta):
                Row.column_fns = Row.cls.pod.column_group
            else:
                Row.column_fns = {}
                
            if self.db.chatty:
                print 'pod.RawQuery to return the following columns: \n\t' + str(Row.columns) + '\n'
            return self.current_cursor.next()
        else:
            return self.current_cursor.next()

    def get_one(self, error_on_multiple = True):
        objects = [object for object in self]
        if len(objects) == 0:
            return None
        else:
            if error_on_multiple and len(objects) > 1:
                raise PodQueryError, "More than one object returned . . . "
            return objects[0]

class Row(object):
    
    cls         = None
    columns     = None
    column_fns  = None

    def __new__(cls, *args):
        
        new_dict = {}
        if Row.cls is Row:
            inst = object.__new__(Row)
            for i,value in enumerate(args[1]):
                if isinstance(value, unicode):
                    value = str(value)
                new_dict[i] = value
                new_dict[Row.columns[i]] = value
            inst.__dict__.update(new_dict)
            return inst
        else:
            for i,value in enumerate(args[1]):
                name = Row.columns[i]
                if name in Row.column_fns:
                    new_dict[name] = Row.column_fns[name].load(value)
                else:
                    if isinstance(value, unicode):
                        value = str(value)
                    new_dict[name] = value    
            return Row.cls(**new_dict)                    
              
    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __setitem__(self, key, value):
        self.__dict__[key] = value
                
