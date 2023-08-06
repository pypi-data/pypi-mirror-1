import exceptions

import core
import typed
import query
import fn
import sqlite3

class PodListError(exceptions.BaseException):
    pass

class PodDictError(exceptions.BaseException):
    pass

class PodSetError(exceptions.BaseException):
    pass

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""" List """""""""""""""""""""""""""                        
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""                             
class List(core.Object):
    
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
    
    def __contains__(self, x):
        get_one = query.RawQuery(where = (ListItem.parent == self) & (ListItem.value == x)).get_one(error_on_multiple = False)
        return True if get_one else False
            
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
                new_list = [item.value for item in query.Query(select = ListItem.value, where = ListItem.parent == self, limit = limit, offset = offset)]
                if i.step is None:
                    return new_list
                else:
                    return new_list[::i.step]
            # here, returning raw list the using the slice that was passed in 
            return [value for value in self][i]
        else:
            raise PodListError, "'" + str(i) + "' not allowed as index, only int/slices allowed . . ."
            
    def __setitem__(self, i, item):
        if isinstance(i, int):
            self.get_set_del_item(i, item)
        else:
            setted = [item for item in self]
            setted.__setitem__(i, item)
            self.clear()
            self.extend(setted)
            
    def __delitem__(self, i):
        if isinstance(i, int):
            self.get_set_del_item(i, delete = True)
        else:
            deleted = [item for item in self]
            deleted.__delitem__(i)
            self.clear()
            self.extend(deleted)
                
    def get_set_del_item(self, i, item = None, delete = False, return_node = False):
        if i < 0: 
            order_by = ListItem.id.desc()
            offset   = -1*i + -1
        else:
            order_by = None
            offset   = i
        selector = ListItem.value if item is None and delete is False else None
        list_item = query.Query(select = selector, limit = 1, where = ListItem.parent == self, order_by = order_by, offset = offset).get_one()
        if list_item  and item is None and delete is False:
            return list_item.value if return_node is False else list_item
        elif list_item and item and delete is False:
            list_item.value = item
        elif list_item and delete:
            list_item.delete()
        else:
            raise IndexError, "list index out of range"
        
    def copy(self):
        return [i for i in self]
        
    def clear(self):
        (ListItem.parent == self).delete()

    def append(self, value):
        ListItem(parent = self, value = value)

    def extend(self, L):
        for value in L:
            ListItem(parent = self, value = value)

    def pre_delete(self):
        self.clear()

    
    def pop(self, i = -1):
        # Remove the item at the given position in the list, and return it. If no index is specified, a.pop(self, ): removes and returns the last item in the def  (self, The square brackets around the i in the method signature denote that the parameter is optional, not that you should type square brackets at that position. You will see this notation frequently in the Python Library Reference.):
        item   = self.get_set_del_item(i = i, return_node = True)
        value = item.value
        item.delete()
        return value
        
    def remove(self, x):
        get_one = query.Query(where = (ListItem.parent == self) & (ListItem.value == x)).get_one(error_on_multiple = False)
        if get_one:
            get_one.delete()
        else:
            raise PodListError, "Item '" + str(x) + "' not in list . . ."
        
    def count(self, x):
        return query.RawQuery(select = fn.count(ListItem.id) >> 'count', where = (ListItem.parent == self) & (ListItem.value == x)).get_one().count

    def index(self, x):
        get_one = query.RawQuery(where = (ListItem.parent == self) & (ListItem.value == x)).get_one(error_on_multiple = False)
        if get_one:
            return query.RawQuery(select = fn.count(ListItem.id) >> 'count', where = ListItem.id < get_one.id).get_one().count            
        else:
            raise PodListError, "Item '" + str(x) + "' not in list . . ."

    """ Not fast """
    def insert(self, i, x):
        inserted = [item for item in self]
        inserted.insert(i,x)
        self.clear()
        self.extend(inserted)
   
    def sort(self):
        sorted = [item for item in self]
        sorted.sort()
        self.clear()
        self.extend(sorted)

    def reverse(self):
        reversed = [item for item in self]
        reversed.reverse()
        self.clear()
        self.extend(reversed)
       
class ListItem(core.Object):
    
    parent = typed.PodObject(index = True)
    value  = typed.Object(index = False)
                        
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""" Dict """""""""""""""""""""""""""                        
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""                               
class Dict(core.Object):
    
    def __init__(self, dict = None, **kwargs):
        core.Object.__init__(self, **kwargs)
        if dict:
            self.update(other = dict)

    def __len__(self):
        get_one = query.RawQuery(select = fn.count(DictItem.id) >> 'count', where = DictItem.parent == self).get_one()
        if get_one:
            return get_one.count
        else:
            return 0 

    def __getitem__(self, key, return_node = False):
        item = core.Query(select = DictItem.value, where = (DictItem.parent == self) & (DictItem.key == key)).get_one()
        if item:
            return item.value
        else:
            raise KeyError                
    
    def __setitem__(self, key, value):
        item = ((DictItem.parent == self) & (DictItem.key == key)).get_one()
        if item:
            item.value = value
        else:
            DictItem(parent = self, key = key, value = value)

    def __contains__(self, key):
        return True if ((DictItem.parent == self) & (DictItem.key == key)).get_one() else False

    def __iter__(self):
        return self.iterkeys()

    def update(self, other):        
        for key,value in other.iteritems():
            self[key] = value
    
    def clear(self):
        (DictItem.parent == self).delete()

    def copy(self):
        return dict([(key,value) for key,value in self.iteritems()])

    def get(self, key, default = None):
        try:
            return Query(select = DictItem.value, where = (DictItem.parent == self) & (DictItem.key == key)).get_one().value
        except KeyError:
            return default
    
    def setdefault(self, key, default):
        try:
            return Query(select = DictItem.value, where = (DictItem.parent == self) & (DictItem.key == key)).get_one().value
        except KeyError:
            self.__setitem__(self, key, default)
            return default
        
    def keys(self):
        return [item.key for item in core.Query(select = DictItem.key, where = DictItem.parent == self)]
    
    def iterkeys(self):
        return (item.key for item in core.Query(select = DictItem.key, where = DictItem.parent == self))

    def values(self):
        return [item.value for item in core.Query(select = DictItem.value, where = DictItem.parent == self)]
    
    def itervalues(self):
        return (item.value for item in core.Query(select = DictItem.value, where = DictItem.parent == self))
    
    def items(self):
        return [(item.key,item.value) for item in core.Query(select = DictItem.key | DictItem.value, where = DictItem.parent == self)]
    
    def iteritems(self):
        return ((item.key,item.value) for item in core.Query(select = DictItem.key | DictItem.value, where = DictItem.parent == self))

    """ Not Supported """
    def fromkeys(self):
        raise PodDictError, "method fromkeys not implemented . . ."

    def has_key(self):
        raise PodDictError, "method has_key not implemented, use 'in' or __contains__ instead . . ."
    
    def pop(self, key, *args, **kwargs):
        raise PodDictError, "method pop is not implemented . . ."

    def popitem(self):
        raise PodDictError, "method popitem is not implemented . . ."
        
class DictItem(core.Object):
    
    parent = typed.PodObject(index = True)
    key    = typed.Object(index = True)
    value  = typed.Object(index = False)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""" Set """""""""""""""""""""""""""                        
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""      
class Set(core.Object):
    
    def __init__(self, set = None, **kwargs):
        core.Object.__init__(self, **kwargs)
        if set:
            self.update(set)
        
    def __len__(self):
        # Return the cardinality of set s.
        get_one = query.RawQuery(select = fn.count(SetItem.id) >> 'count', where = SetItem.parent == self).get_one()
        if get_one:
            return get_one.count
        else:
            return 0 

    def __contains__(self, value):
        #Test x for membership in s. 
        return True if ((SetItem.parent == self) & (SetItem.value == value)).get_one() else False

    def __iter__(self):
        return (item.value for item in core.Query(select = SetItem.value, where = SetItem.parent == self))

    def copy(self):
        return set([item.value for item in core.Query(select = SetItem.value, where = SetItem.parent == self)])

    def update(self, other):
        for elem in other:
            self.add(elem = elem)
    
    def add(self, elem):
        item = core.Query(where = (SetItem.parent == self) & (SetItem.value == elem)).get_one()
        if item:
            item.value = elem
        else:
            SetItem(parent = self, value = elem)     

    def remove(self, elem):
        item = core.Query(where = (SetItem.parent == self) & (SetItem.value == elem)).get_one()
        if item:
            item.delete()
        else:
            raise KeyError

    def discard(self,elem):
        item = core.Query(where = (SetItem.parent == self) & (SetItem.value == elem)).get_one()
        if item:
            item.delete()

    def pop(self):
        item = core.Query(select = SetItem.value, where = SetItem.parent == self, limit = 1).get_one()
        if item:
            value = item.value
            item.delete()
            return value
        else:
            raise KeyError

    def clear():        
        (SetItem.parent == self).delete()

    """ SET OPERATIONS """
    def isdisjoint(self, other):
        #Return True if the set has no elements in common with other. Sets are disjoint if and only if their intersection is the empty set.
        pass

    """ <= """
    def __le__(self, other):
        return self.issubset(other)
    
    def issubset(self, other):
        # set <= other.  Test whether every element in the set is in other.
        return set([e for e in self]).issubclass(other)
    
    """ < """   
    def __lt__(self, other):
        #set < other.  Test whether the set is a true subset of other, that is, set <= other and set != other.
        return set([e for e in self]) < other
    
        
    """ >= """   
    def __ge__(self, other):
        return self.issuperset(other)

    def issuperset(other):
        # set >= other.  Test whether every element in other is in the set.
        super = True
        for elem in other:
            item = core.Query(where = (SetItem.parent == self) & (SetItem.value == elem)).get_one()
            if item is None:
                super = False
        return super
    
    """ > """   
    def __gt__(self, other):
        # set > other.  Test whether the set is a true superset of other, that is, set >= other and set != other.
        set([e for e in self]) > other
        
    """ | """  
    def __or__(self, other):
        return self.union(other)
    
    def union(self, other):
        #union(other, ...) set | other | ... Return a new set with elements from the set and all others.
        # Changed in version 2.6: Accepts multiple input iterables.
        return set([e for e in self]).union(other) 

    """ & """                
    def __and__(self, other):
        return self.intersection(other)
    
    def intersection(self, other):
        #set & other & ... Return a new set with elements common to the set and all others.
        # Changed in version 2.6: Accepts multiple input iterables.
        return set([e for e in self]).intersection(other) 

    """ - """                        
    def __sub__(self, other):
        return self.difference(self, other)
    
    def difference(self, other):
        # difference(other, ...) set - other - ... Return a new set with elements in the set that are not in the others.
        # Changed in version 2.6: Accepts multiple input iterables.
        set([e for e in self]).difference(other)

    """ ^ """                        
    def __xor__(self, other):
        return self.symmetric_difference(other)
    def symmetric_difference(other):
        #set ^ other
        #Return a new set with elements in either the set or other but not both.
        set([e for e in self]).symmetric_difference(other)

    def intersection_update(self, other):
        raise PodSetError, "method intersection_update is not implemented . . ."

    
    def difference_update(self, other):
        raise PodSetError, "method difference_update is not implemented . . ."
    
    def symmetric_difference_update(self, other):
        raise PodSetError, "method symmetric_difference_update is not implemented . . ."

class SetItem(core.Object):
    
    parent = typed.PodObject(index = True)
    value  = typed.Object(index = True)
