import datetime
from util import DictProperty
from meta import TrackableMeta

__all__ = ( 'XMLValue', 'XMLDateTime', 'XMLList' )

class XMLValue( object ):
    __metaclass__ = TrackableMeta
    
    def __init__( self, value = None, name = None, attrs = dict(), required = False, *args, **kwargs ):
        super( XMLValue, self ).__init__( *args, **kwargs )
        self.name = name
        self.value = value
        self.attrs = DictProperty( attrs )
        self.required = required
    
    def __get__( self, parent, cls ):
        """returns self so we can still access the instance"""
        return self
    
    def __set__( self, parent, value ):
        """set self.value when something is assigned to us"""
        self.value = value
    
    def __delete__( self, parent ):
        """clear self.value"""
        self.value = None
        self.attrs = DictProperty()
    
    def __setitem__( self, name, value ):
        if name == 'attr':
            setattr( self, name, DictProperty( value ) )
        else:
            super( XMLValue, self ).__setattr( name, value )
    
    def toxml( self ):
        if not self.required and not self.value and not self.attrs:
            return
        assert self.name, "value has no name: %r" % self
        yield '<' + self.name
        for attr, value in self.attrs.iteritems():
            yield ' %s="%s"' % ( attr, value )
        if self.value is not None:
            yield '>%s</%s>' % ( self.value, self.name )
        else:
            yield ' />'
    
    def __str__( self ):
        return ''.join( self.toxml() )


class XMLDateTime( XMLValue ):
    
    @staticmethod
    def _dt2dict( dt ):
        dtdict = dict()
        if not isinstance( dt, datetime.datetime ):
            dt = datetime.datetime.now()
        dtdict['year'] = dt.year
        dtdict['month'] = dt.month
        dtdict['day'] = dt.day
        dtdict['hour'] = dt.hour
        dtdict['minute'] = dt.minute
        dtdict['second'] = dt.second
        dtdict['microsecond'] = dt.microsecond
        dtdict['tzinfo'] = dt.tzinfo
        return dtdict
    
    def __init__( self, *args, **kargs ):
        super( XMLDateTime, self ).__init__( *args, **kargs )
        if len( args ):
            value = args[0]
        else:
            value = kargs.get( 'value', datetime.datetime.now() )
        self.dt = value
        self.format = kargs.get( 'format' )
        self.value = self.format and value.strftime( self.format ) or value.ctime()
    
    def __set__( self, parent, value ):
        assert isinstance( value, (XMLDateTime, datetime.datetime) ), "you must provide a datetime object"
        self.dt = value
        self.value = self.format and value.strftime( self.format ) or value.ctime()
    

class XMLList( XMLValue, list ):
    def __new__( cls, *args, **kargs ):
        return list.__new__( XMLList, *args )
    
    def __init__( self, *args, **kargs ):
        self.type = kargs.get( 'type', XMLValue )
        if 'type' in kargs:
            del kargs['type']
        super( XMLList, self ).__init__( *args, **kargs )
    
    def append( self, value, attrs = dict() ):
        if not isinstance( value, (XMLValue, XMLNode) ):
            value = self.type( value, self.name, attrs )
        super( XMLList, self ).append( value )
    
    def insert( self, value, attrs = dict() ):
        if not isinstance( value, (XMLValue, XMLNode) ):
            value = XMLValue( value, self.name, attrs )
        super( XMLList, self ).insert( value )
    
    def toxml( self ):
        for value in self:
            for x in value.toxml():
                yield x

# prevent recursive import
from main import XMLNode
