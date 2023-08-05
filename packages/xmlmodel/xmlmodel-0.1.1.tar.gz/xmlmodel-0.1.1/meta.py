import itertools

__all__ = ( 'TrackableMeta',
            'TrackerMeta',
            'TrackableTrackerMeta' )

class TrackableMeta( type ):
    _counter = itertools.count()
    
    def __init__( cls, name, bases, attrs ):
        super( TrackableMeta, cls ).__init__( name, bases, attrs )
        cls._creation_number = cls.__class__._counter.next()

    def __call__( cls, *args, **kargs ):
        obj = cls.__new__( cls, *args, **kargs )
        cls.__init__( obj, *args, **kargs )
        obj._creation_number = cls._counter.next()
        return obj
    

class TrackerMeta( type ):
    def __init__( cls, name, bases, attrs ):
        super( TrackerMeta, cls ).__init__( name, bases, attrs )

        attrs_order = [(a, v._creation_number) for (a, v) in attrs.items()
                       if hasattr( v, '_creation_number' )]

        cls._order = [a[0] for a in sorted( attrs_order, key=lambda x: x[1] )]

    def __iter__( cls ):
        for name in cls._order:
            yield getattr( cls, name )
    
class TrackableTrackerMeta( TrackableMeta, TrackerMeta ):
    pass

##############################################################################
#       Test Cases                                                           #
##############################################################################

def TestTracker():
    class Node:
        __metaclass__ = TrackableTrackerMeta
    
    class Value:
        __metaclass__ = TrackableMeta

    class A( Node ):
        b = Value()
        c = Value()
        class D( Node ):
            e = Value()
            f = Value()
            class G( Node ):
               h = Value()
               i = Value()
               j = Value()
            k = Value()
            l = Value()
        m = Value()
        n = Value()
    
    assert A._order == ['b','c','D','m','n']
    print A._order
    
    assert A.D._order == ['e', 'f', 'G', 'k', 'l']
    print A.D._order
    
    assert A.D.G._order == ['h', 'i', 'j']
    print A.D.G._order
