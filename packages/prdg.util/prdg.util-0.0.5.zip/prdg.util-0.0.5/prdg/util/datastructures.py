from UserDict import DictMixin

class OneValueDict(DictMixin):
    """
    A dict mapping from a set of keys to an unique value. In other words
    d[k] == V, for every k in d. The unique value is changed by changing the
    value for any key in the dict or by setting the value attribute.
    """    
    
    value = None
    """The unique value in the dict."""
    
    key_set = None
    """The set of keys in the dict."""
    
    def __init__(self, key_set, value):
        """
        Construct a new OneValueDict.
        
        Arguments:
        value -- The value for every key in the dict.
        key_set -- The set of keys.
        """
        self.value = value
        self.key_set = key_set
    
    def __getitem__(self, key):
        if key in self.key_set:
            return self.value
        
        raise KeyError(key)
    
    def __setitem__(self, key, item):        
        self.key_set.add(key)
        self.value = item        
        
    def __delitem__(self, key):
        self.key_set.remove(key)
    
    def keys(self):
        return self.key_set

def identity_dict(keys):
    return dict((k, k) for k in keys)

class AddItemsDictWrapper(DictMixin):
    """
    A wrapper around a dict that adds new items to the dict. The added items
    override existing items with the same key. Also the added items are
    read-only.
    """
    
    def __init__(self, d, new_items={}, **kwargs):
        """
        Arguments:
        d -- The dict to be wrapped.
        new_items -- A dict containing new items to be added.
        kwargs -- Same as `new_items`.
        """
        self.d = d
        self.new_items = {}
        self.new_items.update(new_items, **kwargs)
    
    def _check_key(self, key):
        if key in self.new_items:
            raise KeyError('This item is read-only.', key)        
    
    def __getitem__(self, key):
        if key in self.new_items:
            return self.new_items[key]
        
        return self.d.__getitem__(key)
    
    def __setitem__(self, key, item):  
        self._check_key(key)              
        return self.d.__setitem__(key, item)
        
    def __delitem__(self, key):
        self._check_key(key)        
        return self.d.__delitem__(key)
    
    def keys(self):
        return list(self.d.keys()) + list(self.new_items.keys())

class HideItemsDictWrapper(DictMixin):
    """A wrapper around a dict that remove keys from it."""
    
    def __init__(self, d, hidden_keys_set):
        self.d = d
        self.hidden_keys = hidden_keys_set
    
    def _check_key(self, key):
        if key in self.new_items:
            raise KeyError('This key is hidden.', key)   
    
    def __getitem__(self, key):
        self._check_key(key)
        return self.d.__getitem__(key)
    
    def __setitem__(self, key, item):  
        self._check_key(key)
        return self.d.__setitem__(key, item)
        
    def __delitem__(self, key):
        self._check_key(key)
        return self.d.__delitem__(key)
    
    def keys(self):
        return list(set(self.d.keys()) - self.hidden_keys)  
    
def is_ordered(seq, key=lambda x: x, cmp=cmp):    
    if not seq:
        return True
    
    previous = key(seq[0])
    for e in seq[1:]:
        e = key(e)
        if cmp(e, previous) < 0:
            return False
        previous = e 
    
    return True
    
if __name__ == '__main__':
    d = OneValueDict(set([2, 5]), 'value')
    print d[2]
    print d[5]
    
    d[8] = 0
    
    for k in d:
        print k
    
    for k, v in d.iteritems():
        print k, v   
        
