import inspect
from copy import copy, deepcopy
from util import DictProperty
from meta import TrackableTrackerMeta

__all__ = ( 'XMLNode', 'XMLModel', 'XMLNodeList' )

class XMLNode( object ):
    """The base type for all your nodes"""
    
    __metaclass__ = TrackableTrackerMeta
    
    def __init__( self ):
        # Set the tagname from the class name
        if not hasattr( self, '_name' ):
            self._name = self.__class__.__name__
        
        # Get the XMLAttrs inner class, and collect it's properties
        attrs = getattr( self, 'XMLAttrs', None )
        attrs = getattr( attrs, '__dict__', None )
        if attrs:
            self.XMLAttrs = DictProperty(
                item for item in attrs.iteritems() if not item[0].startswith( '_' )
            )
        else:
            self.XMLAttrs = DictProperty()
        
        # Collect XMLNode inner classes, create instances, and add to self.values
        ### test to make sure references are retained, and no copies made ###
        props = dict( ( id( v ), k ) for k, v in self.__class__.__dict__.iteritems() )
        self.values = list()
        for name in self._order:
            if name.startswith( '_' ):
                continue
            prop = getattr( self, name )
            if inspect.isclass( prop ) and issubclass( prop, XMLNode ):
                newprop = prop()
                setattr( self, name, newprop )
                self.add( newprop )
            elif isinstance( prop, XMLValue ):
                prop.name = name
                self.add( prop )
        
    
    def add( self, value ):
        self.values.append(value)
    
    def toxml( self ):
        yield "<%s" % self._name
        for attr, value in self.XMLAttrs.iteritems():
            yield ' %s="%s"' % ( attr, value )
        yield '>'
        for v in self.values:
            for x in v.toxml():
                yield x
        yield "</%s>" % self._name
    
    def __str__( self ):
        return ''.join( self.toxml() )
    

class XMLModel( XMLNode ):
    """The root of your XML document, extends XMLNode"""
    
    def toxml( self ):
        yield '<?xml version="1.0"?>\n'
        for x in super( XMLModel, self ).toxml():
            yield x
    
    def __str__( self ):
        return ''.join( self.toxml() )
    

class XMLNodeList( XMLNode, list ):
    """XMLNodeList( name ): This class is supposed to be a list of XMLNodes,
    but it can contain XMLValues also. It does not have it's own containing
    tag, rather, the new() methods creates instances of XMLNode with the given
    name"""
    
    def append( self, value ):
        assert isinstance( value, ( XMLNode, XMLValue ) )
        super( XMLNodeList, self ).append( value )
    
    def insert( self, index, value ):
        assert isinstance( value, ( XMLNode, XMLValue ) )
        super( XMLNodeList, self ).insert( index, value )
     
    def __setitem__( self, index, value ):
        assert isinstance( value, ( XMLNode, XMLValue ) )
        super( XMLNodeList, self ).__setitem__( index, value )
    
    def new( self, attrs = dict() ):
        "Create a new node, add to the list, and return a reference"
        # add immutable objects to the class
        attrs = dict()
        for name, value in self.__class__.__dict__.iteritems():
            try:
                hash( value )
                attrs[name] = copy( value )
            except TypeError:
                pass
        NodeClass = type( self.__class__.__name__, (XMLNode,), attrs )
        NodeClass._order = self.__class__._order
        
        # add mutable objects to the instance
        node = NodeClass.__new__( NodeClass )
        for name in self.__class__._order:
            value = getattr( self.__class__, name )
            try:
                hash( value )
            except TypeError:
                setattr( node, name, copy( value ) )
        node.XMLAttrs = attrs
        
        node.__init__()
        self.append( node )
        return node
    
    def toxml( self ):
        for node in self:
            for x in node.toxml():
                yield x
    
    def __str__( self ):
        return ''.join( self.toxml() )
    
# prevent recursive import
from xmlvalues import XMLValue
