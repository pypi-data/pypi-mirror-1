import exceptions

import time
import datetime
 
import core
from db import Pickler
from query import Query, PodQueryError

unique = 'U'

class PodTypeError(exceptions.BaseException):
    pass

class Expression(object):
    
    def __init__(self, left = None, right = None, op = None, parens = True):            
        self.left    = left
        self.right   = right
        self.op      = op
        self.parens  = parens
    
    def get_sql(self, full_name = False, type = None):
        
        self.expression = ""
        self.args       = []
        self.class_pods = set()
        self.full_name  = full_name
        #type includes select, raw_select, where, group_by, order_by
        self.type       = type
        
        self.get_my_sql(head = self)

    def get_my_sql(self, head):
        
        """ left """
        if head.type == 'where' and self.parens:
            head.expression += "("
            
        if isinstance(self.left, Expression):
            self.left.get_my_sql(head = head)
        elif self.left is not None:
            self.process_arg(head = head, value = self.left, left = True)

        # HANDLES TypedCondition | DynamicCondition mismatch
        if isinstance(self.left, DynamicCondition): # and not isinstance(self.right, DynamicCondition):
            head.expression = '(id IN (SELECT fid FROM %kvdict% WHERE ' + head.expression + '))'
            
        if self.op is not None:
            head.expression += self.op
        else:
            raise PodTypeError, "Expression must be either terminal or have an operation . . . "

        # HANDLES TypedCondition | DynamicCondition mismatch
        # if not isinstance(self.left, DynamicCondition) and isinstance(self.right, DynamicCondition):
        if isinstance(self.right, DynamicCondition):
            head.expression += '(id IN (SELECT fid FROM %kvdict% WHERE ' 
            close_kv = True
        else:
            close_kv = False
        
        """ right """
        if isinstance(self.right, Expression):
            self.right.get_my_sql(head = head)
        elif self.right is not None:
            self.process_arg(head = head, value = self.right)

        # HANDLES TypedCondition | DynamicCondition mismatch
        if close_kv:
            head.expression += '))'

        if head.type == 'where' and self.parens: 
            head.expression += ")"
     
    def process_arg(self, head, value, left = False):
        if isinstance(value, Expression):
            value.get_my_sql(head = head)
        elif left is True:
            head.expression += str(value)
        elif isinstance(value, core.Object):
            head.expression += "?"
            head.args.append(value.get_full_id())
        elif isinstance(value, bool):
            head.expression += "?"
            head.args.append(int(bool(value)))
        elif isinstance(value, (list,set)):
            head.expression += "("
            for item in value:
                self.process_arg(head = head, value = item)
                head.expression += ","
            head.expression = head.expression[:-1] + ")"    
        else:
            head.expression += "?"
            head.args.append(value)
        
    """ EXPRESSION CHAINING """
    def __and__(self, other):
        raise PodTypeError, "The INTERSECT '&' operator not supported on column expressions . . . "
    
    def __or__(self, other):
        return Expression(left = self, right = other, op = ',')
    
    def __iter__(self):
        return Query(where = self).__iter__()

    def delete(self):
        return Query(where = self).delete()
    
    def get_one(self, error_on_multiple = True):
        return Query(where = self).get_one(error_on_multiple = error_on_multiple)

class DynamicCondition(Expression):
    
    def get_sql(self, full_name = False, type = None):
        Expression.get_sql(self, full_name = full_name, type = type)
        if self.right is None or isinstance(self.right, DynamicCondition):
            self.expression = 'id IN (SELECT fid FROM %kvdict% WHERE ' + self.expression + ')'
        
    def __and__(self, other):
        return DynamicCondition(left = self, right = other, op = ' AND ')

    def __or__(self, other):
        return DynamicCondition(left = self, right = other, op = ' OR ')

class Dynamic(DynamicCondition):
    
    def __init__(self, cls_pod, name):
        DynamicCondition.__init__(self, left = self)
        self.cls_pod = cls_pod
        self.name    = name
        self.pickler = cls_pod.db.pickler
        self.slice   = None
        
    def get_my_sql(self, head):        
        if head.type != 'where':
            raise PodQueryError, "You can only use dynamic attributes in a 'where' statement . . . "
        head.expression += '(key=?)'
        head.args.append(self.name)
        head.class_pods.add(self.cls_pod)
    
    def dump(self, value):
        return Pickler.dump(value)
    
    def __eq__(self, value):
        if value is None:
            return self & DynamicCondition(left = 'value', op = ' IS NULL', right = None)
        else:
            if self.slice is None:
                return self & DynamicCondition(left = 'value', op = '=', right = Pickler.dump(value))
            else:
                if value.__class__ is not str:
                    raise PodQueryError, "Value must be string for string comparison on dynamic type . . . "
                sub = str(self.slice[0]) if self.slice[1] is None else str(self.slice[0]) + ',' + str(self.slice[1])
                return self & DynamicCondition(left = "substr(value,1,1)='s' AND substr(value," + sub + ")", op = '=',   right = value)
           
    def __ne__(self, value):
        if value is None:
            return self & DynamicCondition(left = 'value', op = 'IS NOT NULL', right = None)
        else:
            return self & DynamicCondition(left = 'value', op = '<>', right = Pickler.dump(value))
    
    def is_in(self, value):
        
        if isinstance(value, (list, set, tuple, frozenset)):
            return self & DynamicCondition(left = 'value', op = ' IN ', right = [self.dump(item) for item in value])
        else:
            raise PodTypeError, "value: '" + str(value) + "' must be list, set, frozenset, or tuple'"
       
    def __gt__(self, value):
        return self.get_dynamic_compare(op = '>', value = value)

    def __ge__(self, value):
        return self.get_dynamic_compare(op = '>=', value = value)

    def __lt__(self, value):
        return self.get_dynamic_compare(op = '<', value = value)

    def __le__(self, value):
        return self.get_dynamic_compare(op = '<=', value = value)
        
    def contains(self, value):
        return self.get_string_compare('%' + str(value) + '%')
    
    def startswith(self, value):
        return self.get_string_compare(str(value) + '%')
    
    def endswith(self, value):
        return self.get_string_compare('%' + str(value))
    
    def __getitem__(self, item):        
        self.slice = (get_string_slice(item, offset = 1))
        return self
    
    def get_dynamic_compare(self, op, value):
        return self & DynamicCondition(left = "(substr(value,1,1)='i' OR substr(value,1,1)='f') AND 1*substr(value,2)", op = op, right = value)

    def get_string_compare(self, value):    
        if value.__class__ is not str:
            raise PodQueryError, "Value must be string for string comparison on dynamic type . . . "
        return self & DynamicCondition(left = "substr(value,1,1)='s' AND substr(value,2)", op = ' LIKE ',   right = value)

""" ############################################################################################
###
###    THE TYPES
###
""" ############################################################################################

class TypedExpression(Expression):
    
    """ THE AS NAME NAMING OPERATOR """
    def __rshift__(self, as_name):
        #if self.as_name and as_name:
        #    raise PodTypeError, "You tried to set column expression to '" + as_name + "' but it's already set to '" + str(self.as_name) + "' . . . "
        return AsName(left = self, right = None, op = ' AS ' + as_name + ' ')
    
    """ MATH OPERATORS """
    def __add__(self, other):
        return Math(left = self, right = other, op = '||' if isinstance(other, str) else ' + ' )
    def __radd__(self, other):
        return Math(left = other, right = self, op = '||' if isinstance(other, str) else ' + ' )
    def __sub__(self, other):
        return Math(left = self, right = other, op = "-")
    def __rsub__(self, other):
        return Math(left = other, right = self, op = "-")
    def __mul__(self, other):
        return Math(left = self, right = other, op = "*")
    def __rmul__(self, other):
        return Math(left = other, right = self, op = "*")
    def __div__(self, other):
        return Math(left = self, right = other, op = "/")
    def __rdiv__(self, other):
        return Math(left = other, right = self, op = "/")
    
    """ COMPARISON OPERATORS """
    """ The basics """ 
    def __eq__(self, value):
        if value is None:
            return TypedCondition(left = self, op = ' IS NULL', right = None)
        else:
            return TypedCondition(left = self, op = '=', right = value)

    def __ne__(self, value):
        if value is None:
            return TypedCondition(left = self, op = 'IS NOT NULL', right = None)
        else:
            return TypedCondition(left = self, op = '<>', right = value)

    def is_in(self, value):
        # value will be list, will be parsed by get_sql function
        return TypedCondition(left = self, op = ' IN ', right = value) 

    """ Really, only for strings """     
    def contains(self, value):
        return TypedCondition(left = self, op = ' LIKE ',   right = '%' + str(value) + '%')
    
    def startswith(self, value):
        return TypedCondition(left = self, op = ' LIKE ',   right = str(value) + '%')
    
    def endswith(self, value):
        return TypedCondition(left = self, op = ' LIKE ', right = '%' + str(value))
    
    def __getitem__(self, item):
        import fn
        start,length = get_string_slice(item, offset = 0)
        return fn.substr(self, start,length)
        
    """ Really, only for numbers """     
    def __gt__(self, value):
        return TypedCondition(left = self, op = ' > ',  right = value)
    
    def __ge__(self, value):
        return TypedCondition(left = self, op = ' >= ', right = value)
    
    def __lt__(self, value):
        return TypedCondition(left = self, op = ' < ',  right = value)
      
    def __le__(self, value):
        return TypedCondition(left = self, op = '<= ', right = value)

    def between(self, low, high):
        return TypedCondition(left = self, op = ' BETWEEN ', right = TypedCondition(left = low, right = high, op = ' AND ', parens = False))
    
    """ order by """
    def asc(self):
        return OrderAsc(col = self)
    
    def desc(self):
        return OrderDesc(col = self)
        
class AsName(TypedExpression):
    
    def get_my_sql(self, head):
        if head.type != 'select':
            raise PodTypeError, "You cannot use AS operator '>>' in anything but the select statement . . ."
        return Expression.get_my_sql(self, head)
    
class Math(TypedExpression):
    
    def __init__(self, left = None, right = None, op = None, parens = True):    
        self.left    = left
        self.right   = right
        self.op      = op
        self.parens  = parens

class TypedCondition(TypedExpression):
    
    def __init__(self, left = None, right = None, op = None, parens = True):            
        self.left    = left
        self.right   = right
        self.op      = op
        self.parens  = parens
        
    def __and__(self, other):
        return TypedCondition(left = self, right = other, op = ' AND ')

    def __or__(self, other):
        return TypedCondition(left = self, right = other, op = ' OR ')
    
class Type(TypedExpression):

    def __init__(self, index = False, cls_pod = None, name = None):        
        Expression.__init__(self)
        self.index = index
        if cls_pod and name:
            self.cls_pod = cls_pod
            self.name    = name

    def __getstate__(self):
        return {'index': self.index}
         
    def on_db_activate(self, db):
        pass
            
    def drop(self):
        self.cls_pod.column_drop_and_delete_forever(self)
            
    def get_deep_copy(self, cls_pod, name):
        return self.__class__(index = self.index, cls_pod = cls_pod, name = name)
        
    def on_pod_init(self, cls_pod, name):
        self.cls_pod = cls_pod
        self.name    = name
               
    def get_alter_table(self):
        return self.name + " " + self.db_type
    
    def dump(self, value):
        return None if value is None else self.py_type(value)
    
    def load(self, value):
        return None if value is None else self.py_type(value)
    
    def is_same_column_type(self, other):
        return other.index == self.index and other.__class__ is self.__class__
    
    def get_my_sql(self, head):
        head.expression += self.get_sql_column_name(head = head)
        head.class_pods.add(self.cls_pod)
                   
    def get_sql_column_name(self, head):
        return self.cls_pod.table + '.' + self.name if head.full_name else self.name
            
""" Objects -- This is a biggie! """
class Object(Type):

    db_type = 'TEXT'
    
    def on_db_activate(self, db):
        self.pickler = db.pickler
                           
    def dump(self, value):
        return Pickler.dump(value)
    
    def load(self, value):
        return self.pickler.load(value)
    
    """ all objects """
    def __eq__(self, value):
        if value is None:
            return TypedCondition(left = self, op = ' IS NULL', right = None)
        else:
            return TypedCondition(left = self, op = '=', right = Pickler.dump(value))

    def __ne__(self, value):
        if value is None:
            return TypedCondition(left = self, op = 'IS NOT NULL', right = None)
        else:
            return TypedCondition(left = self, op = '<>', right = Pickler.dump(value))
    
    def is_in(self, value):
        if isinstance(value, (list, set, tuple, frozenset)):
            return TypedCondition(left = self, op = ' IN ', right = [self.dump(item) for item in value])
        else:
            raise PodTypeError, "value: '" + str(value) + "' must be list, set, frozenset, or tuple'"


""" It's so common . . .  """
class PodObject(Type):
    
    db_type = 'TEXT'
    
    def on_db_activate(self, db):
        self.cache = db.cache
                           
    def dump(self, value):
        if isinstance(value, core.Object):
            return value.get_full_id()
        elif value is None:
            return None
        else:
            raise PodTypeError, "Value '" + str(value) + "' is not of type pod.Object . . . "
    
    def load(self, value):
        if value:
            value = value.split(":")
            return self.cache.get_inst(cls_id = int(value[0]), inst_id = int(value[1]))
        else:
            return None
                   
""" Boolean """
class Boolean(Type):
    
    db_type = 'INTEGER'

    def dump(self, value):
        return None if value is None else int(bool(value))
    
    def load(self, value):
        return None if value is None else bool(value)

""" String """    
class String(Type):
    
    db_type = 'TEXT'
    py_type = str
        
""" Numbers """
class Int(Type):
    db_type = 'INTEGER'
    py_type = int

class Float(Type):
    db_type = 'REAL'
    py_type = float

# can be True, False, None

""" Special columns that do automagic things """
class Time(Int):
    
    @staticmethod
    def utc_timestamp(): 
        #old way -- t = datetime.datetime.utcnow() return time.mktime(t.timetuple()) +1e-6*t.microsecond
        return int(time.mktime(datetime.datetime.utcnow().timetuple()))
    
    def __init__(self, index = False, date_string = False, local_time = True, convert_time_stamp = True, cls_pod = None, name = None):
        Int.__init__(self, index = index, cls_pod = cls_pod, name = name)
        self.date_string        = date_string
        self.local_time         = local_time
        self.convert_time_stamp = convert_time_stamp
    
    def on_pod_init(self, cls_pod, name):
        Int.on_pod_init(self, cls_pod = cls_pod, name = name)
        self.utc_offset         = Time.utc_timestamp()-int(time.time())

    def __getstate__(self):
        dict = Int.__getstate__(self)
        for key in ['date_string', 'local_time', 'convert_time_stamp']:
            dict[key] = self.__dict__[key]
        return dict

    def load(self, value):
        if self.date_string and self.convert_time_stamp:
            return self.convert_utc_stamp_to_time(Int.load(self, value))
        else:
            return Int.load(self, value)
    
    def dump(self, value):
        if self.date_string and self.convert_time_stamp:
            return Int.dump(self, self.convert_time_to_utc_stamp(value))
        else:
            return Int.dump(self, value)
                
    def older_than(self, years = 0, weeks = 0, days = 0, hours = 0, minutes = 0, seconds = 0):
        ctime = years*365*24*3600 + weeks*7*24*3600 + days*24*3600 + hours*3600 + minutes*60 + seconds
        return self <= int(Time.utc_timestamp()-ctime)
    
    def younger_than(self, years = 0, weeks = 0, days = 0, hours = 0, minutes = 0, seconds = 0):
        ctime = years*365*24*3600 + weeks*7*24*3600 + days*24*3600 + hours*3600 + minutes*60 + seconds
        return self >= int(Time.utc_timestamp()-ctime)
    
    def pre_dates(self, year = None, month = None, day = None, hour = None, minute = None, second = None, time_stamp = None, local_time = None):
        return self <= self.args_to_epoch(year,month,day,hour,minute,second,time_stamp,local_time if local_time is not None else self.local_time)
        
    def post_dates(self, year = None, month = None, day = None, hour = None, minute = None, second = None, time_stamp = None, local_time = None):
        return self >= self.args_to_epoch(year,month,day,hour,minute,second,time_stamp,local_time if local_time is not None else self.local_time)
    
    def is_date(self, year = None, month = None, day = None, local_time = None):
        local_time = local_time if local_time is not None else self.local_time
        if day:
            year = year if year is not None else datetime.datetime.now().year
            month = month if month is not None else datetime.datetime.now().month
            return self.post_dates(year,month,day,None,None,None,None,local_time) & self.pre_dates(year,month,day+1,None,None,None,None,local_time)
        elif month:
            year = year if year is not None else datetime.datetime.now().year
            return self.post_dates(year,month,day,None,None,None,None,local_time) & self.pre_dates(year,month+1,day,None,None,None,None,local_time)
        elif year:
            return self.post_dates(year,month,day,None,None,None,None,local_time) & self.pre_dates(year+1,month,day,None,None,None,None,local_time)
        else:
            raise PodQueryError, "You did not provide a year, month, or day for is_date . . . "

    def args_to_epoch(self,y,m,d,h,n,s,time_stamp,local_time):        
        if time_stamp and self.date_string is None:
            raise PodQueryError, "You provided a time_stamp '" + str(time_stamp) + "' but this column does not have a date_string convertor set . . . "
        elif time_stamp and self.date_string:
            ctime = time.mktime(time.strptime(time_stamp, self.date_string))
        else:
            y = y if y is not None else datetime.datetime.now().year
            m = m if m is not None else 1
            d = d if d is not None else 1
            h = h if h is not None else 0
            n = n if n is not None else 0
            s = s if s is not None else 0        
            ctime = time.mktime(datetime.datetime(y,m,d,h,n,0).timetuple())+s        
        return int(ctime + int(local_time)*self.utc_offset)
        
    def convert_time_to_utc_stamp(self, value, date_string = None, local_time = None):
        date_string = date_string if date_string is not None else self.date_string
        value = datetime.datetime.fromtimestamp(value) if isinstance(value, (int,float,long)) else value
        value = time.strptime(value, date_string) if date_string else value.timetuple()                  
        return int(time.mktime(value) + self.utc_offset*int(local_time if local_time is not None else self.local_time))
    
    def convert_utc_stamp_to_time(self, value, date_string = None, local_time = None):
        date_string = date_string if date_string is not None else self.date_string
        value = int(value-self.utc_offset*int(local_time if local_time is not None else self.local_time))
        return datetime.datetime.fromtimestamp(value).strftime(date_string) if date_string else value
    
class TimeCreate(Time):
    
    def on_pod_init(self, cls_pod, name):
        Time.on_pod_init(self, cls_pod = cls_pod, name = name)
        cls_pod.type_callbacks_create.add(self)
        
    def on_inst_create(self, inst, kwargs):
        kwargs = {} if kwargs is None else kwargs
        kwargs[self.name] = self.load(Time.utc_timestamp())
        return inst,kwargs
     
class TimeLoad(Time):
    
    def on_pod_init(self,cls_pod,name):
        Time.on_pod_init(self, cls_pod = cls_pod, name = name)
        cls_pod.type_callbacks_load.add(self)        

    def on_inst_create(self, inst, kwargs):
        kwargs = {} if kwargs is None else kwargs
        kwargs[self.name] = self.load(Time.utc_timestamp())
        return inst,kwargs
    
    def on_inst_load(self, inst):
        object.__getattribute__(inst, '__setattr__')(self.name, self.load(Time.utc_timestamp()))
        return inst
        
""" BINARY TYPES """
class Binary(Type):
    
    db_type = 'BINARY'
    
    def dump(self, value):
        return sqlite3.Binary(value)

    def load(self, value):
        return value

class BinaryPickle(Type):
    
    db_type = 'BINARY'
                     
    def on_db_activate(self, db):
        self.pickler = db.pickler
    
    def dump(self, value):
        return self.pickler.bdump(value)

    def load(self, value):
        return self.pickler.load(value)

""" ORDER """
class Order(Expression):
    
    def __init__(self, col):
        Expression.__init__(self)
        self.col = col
        
    
    def get_my_sql(self, head):
        head.expression += self.col.get_sql_column_name(head) + " " + self.TYPE

class OrderAsc(Order):
    TYPE = 'ASC'

class OrderDesc(Order):
    TYPE = 'DESC'
        
def get_string_slice(item, offset = 0):
        if isinstance(item, int):
            item = item if item < 0 else item + 1 + offset
            return item,1
        elif isinstance(item, slice):
            if item.start is None:
                raise PodQueryError, "You must provide start when slicing query attributes . . . "                 
            if item.step:
                raise PodQueryError, "Cannot use step when slicing query attributes . . . "            
            elif item.stop is None:
                item = item.start if item.start < 0 else item.start + 1 + offset
                return item, None
            else:
                count = item.stop - item.start
                if count < 1:
                    raise PodQueryError, "You must provide a positive (left to right) amount of characters when slicing query attributes . . . "            
                item = item.start if item.start < 0 else item.start + 1 + offset
                return item, count



