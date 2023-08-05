import itertools

class DictObj( dict ):
    """A helper class, that acts like a dict and an object."""
    
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    

class DictProperty( DictObj ):
    """A DictObj that also overrides __get__/__set__/__delete__:
    get: returns self,
    set: wraps dict.clear() and dict.update()
    delete: wraps dict.clear()"""
    
    __slots__ = ()
    
    def __get__( self, parent, cls ):
        """returns self so we can still access the instance"""
        return self
    
    def __set__( self, parent, value ):
        """clear and update self when something is assigned to us"""
        value = dict( value )
        self.clear()
        self.update( value )
    
    def __delete__( self, parent ):
        """clear self"""
        self.clear()
