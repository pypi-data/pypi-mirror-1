import exceptions

import core
import column
import query
import fn
import sqlite3

class PodCollectionError(exceptions.BaseException):
    pass


class List(core.Object):
    
    name = column.String(index = True)
    
    def __init__(self, list = None, **kwargs):
        core.Object.__init__(self, **kwargs)
        if list:
            self.extend(list)
        
    def __len__(self):
        get_one = query.RawQuery(select = fn.count(ListItem.id) >> 'count', where = ListItem.parent == self).get_one()
        if get_one:
            return get_one.count
        else:
            return 0 
        
    def __iter__(self):
        return (item.value for item in query.Query(select = ListItem.value, where = ListItem.parent == self))

    def __getitem__(self, i):
        if isinstance(i, int):
            return self.get_set_del_item(i)
        elif isinstance(i, slice):
            start,stop,step = i.start,i.stop,i.step
            if (start >= 0 or start is None) and (stop >=0 or stop is None):
                start = 0 if start is None else start
                offset = start if start > 0 else None
                if stop is None:
                    limit = -1           
                elif stop-start < 0:
                    return []
                else:
                    limit = stop-start if stop is not None else -1
                new_list = [item.value for item in query.Query(select = ListItem.value, limit = limit, offset = offset)]
                if i.step is None:
                    return new_list
                else:
                    return new_list[::i.step]
            # here, returning raw list the using the slice that was pass in 
            return [value for value in self][i]
        else:
            raise PodCollectionError, "'" + str(i) + "' not allowed as index, only int for List and str or int for OrderedDict . . . "
            
    def __setitem__(self, i, item):
        if isinstance(i, int):
            self.get_set_del_item(i, item)
        else:
            setted = [item for item in self]
            setted.__setitem__(i, item)
            self.clear_collection()
            self.extend(setted)
            
    def __delitem__(self, i):
        if isinstance(i, int):
            self.get_set_del_item(i, delete = True)
        else:
            deleted = [item for item in self]
            deleted.__delitem__(i)
            self.clear_collection()
            self.extend(deleted)
        
    def get_set_del_item(self, i, item = None, delete = False):
        if i < 0: 
            order_by = ListItem.id.desc()
            offset   = -1*i + -1
        else:
            order_by = None
            offset   = i
        selector = ListItem.value if item is None and delete is False else None
        list_item = query.Query(select = selector, limit = 1, where = ListItem, order_by = order_by, offset = offset).get_one()
        if list_item  and item is None and delete is False:
            return list_item.value
        elif list_item and item and delete is False:
            list_item.value = item
        elif list_item and delete:
            list_item.delete()
        else:
            raise IndexError, "list index out of range"
        
    def clear_collection(self):
        (ListItem.parent == self).delete()

    def append(self, value):
        ListItem(parent = self, value = value)

    def extend(self, L):
        if isinstance(L, List):
            L = [item for item in L]
        for value in L:
            ListItem(parent = self, value = value)

    def pre_delete(self):
        self.clear_collection()

    def contains(self, item):
        return [item for item in self].contains(item)
    
    def pop(self, i):
        # Remove the item at the given position in the list, and return it. If no index is specified, a.pop(self, ): removes and returns the last item in the def  (self, The square brackets around the i in the method signature denote that the parameter is optional, not that you should type square brackets at that position. You will see this notation frequently in the Python Library Reference.):
        popped = [item for item in self]
        item   = popped.pop(i)
        self.clear_collection()
        self.extend(popped)
        return item
    
    def insert(self, i, x):
        inserted = [item for item in self].remove(x)
        self.clear_collection()
        self.extend(inserted)
    
    def remove(self, x):
        removed = [item for item in self].remove(x)
        self.clear_collection()
        self.extend(removed)
    
    def index(self, x):
        return [item for item in self].index(x)
    
    def count(self, x):
        return [item for item in self].count(x)

    def sort(self):
        sorted = [item for item in self].sort()
        self.clear_collection()
        self.extend(sorted)

    def reverse(self):
        reversed = [item for item in self].reverse()
        self.clear_collection()
        self.extend(reversed)
   
class ListItem(core.Object):
    
    parent = column.Object(index = True)
    value  = column.Pickle(index = False)
                             
class OrderedDict(core.Object):
    
    def __init__(self, dict = None, **kwargs):
        core.Object.__init__(self, **kwargs)
        if dict:
            self.extend(dict)

    def __getitem__(self, key):
        item = core.Query(select = DictItem.value, where = DictItem.key == key).get_one()
        if item:
            return item.value
        else:
            raise KeyError                
    
    def __setitem__(self, key, value):
        item = (DictItem.key == key).get_one()
        if item:
            item.value = value
        else:
            DictItem(parent = self, key = key, value = value)

    def __contains__(self, key):
        return True if (DictItem.key == key).get_one() else False

    def update(self, other):        
        for key,value in other.iteritems():
            self[key] = value
    
    def clear_collection(self):
        (DictItem.parent == self).delete()

    def copy(self):
        pass

    def fromkeys(self):
        raise PodDictError, "method fromkeys not implemented . . ."

    def get(self, key, default = None):
        try:
            return Query(select = DictItem.value, where = DictItem.key == key).get_one().value
        except KeyError:
            return default
    
    def setdefault(self, key, default):
        try:
            return Query(select = DictItem.value, where = DictItem.key == key).get_one().value
        except KeyError:
            self.__setitem__(self, key, default)
            return default
    
    def has_key(self):
        raise PodDictError, "method has_key not implemented, use 'in' or __contains__ instead . . ."
    
    def keys(self):
        return [item.key for item in core.Query(select = DictItem.key, where = DictItem)]
    
    def iterkeys(self):
        return (item.key for item in core.Query(select = DictItem.key, where = DictItem))

    def values(self):
        return [item.value for item in core.Query(select = DictItem.value, where = DictItem)]
    
    def itervalues(self):
        return (item.value for item in core.Query(select = DictItem.value, where = DictItem))
    
    def items(self):
        return [(item.key,item.value) for item in core.Query(select = DictItem.key | DictItem.value, where = DictItem)]
    
    def iteritems(self):
        return ((item.key,item.value) for item in core.Query(select = DictItem.key | DictItem.value, where = DictItem))

    def pop(self, key, *args, **kwargs):
        raise PodDictError, "method pop is not implemented . . ."

    def popitem(self):
        raise PodDictError, "method popitem is not implemented . . ."
        
class DictItem(core.Object):
    
    parent = column.Object(index = True)
    key    = column.String(index = True)
    value  = column.Pickle(index = False)
    


