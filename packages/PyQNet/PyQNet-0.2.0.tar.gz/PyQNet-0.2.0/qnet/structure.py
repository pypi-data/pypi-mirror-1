"""Yet another implementation of a Python struct wrapper"""
import struct,zlib,itertools

__all__ = [
    'Struct',
    'Structure', # alias
    'StructInstance',
    'Byte',
    'UByte',
    'Short',
    'UShort',
    'Int',# alias
    'Integer',
    'UInt',# alias
    'UInteger',
    'ShortFloat',
    'Float',
    'ListOf',
    'String',
    'Unicode',
    'Checksum',
]

class StructInstance( object ):
    """Base class for structure-data instances"""
    _struct = None 
    _encoded = None
    def __init__( self, **named ):
        """Initialize by copying named parameters into dict"""
        self.__dict__.update( named )
    def encode( self ):
        """Encode this instance for transmission"""
        if self._encoded is None:
            self._encoded = self._struct.encode( self )
        return self._encoded
    @classmethod
    def decode( cls, value, offset=0 ):
        """Decode the value into an instance of this class"""
        return cls._struct.decode( value, offset )
    def iteritems( self ):
        for element in self._struct.elements:
            yield element,getattr(self,element.name,None)
    def __repr__( self ):
        return '%s( %s )'%(
            self.__class__.__name__,
            ", ".join( [
                '%s=%r'%(key.name,value)
                for (key,value) in self.iteritems()
            ]),
        )
    def __cmp__( self, other ):
        for a,b in itertools.izip( self.iteritems(), other.iteritems()):
            compare = cmp( a,b )
            if compare:
                return compare 
        return 0
    def __lt__( self, other ):
        return self.__cmp__( other ) == -1
    def __gt__( self, other ):
        return self.__cmp__( other ) == 1
    def __eq__( self, other ):
        return self.__cmp__( other ) == 0
    def __neq__( self, other ):
        return self.__cmp__( other ) != 0

class Struct( object ):
    """Structure definition which packs/unpacks elements"""
    name = None
    def __init__( self, *elements, **named ):
        """Create the structure from set of elements"""
        if named.has_key( 'name' ):
            self.name = named.get( 'name','')
        self.elements = elements 
        for element in elements:
            if getattr(element,'name',None):
                setattr( self, element.name, element )
            else:
                raise ValueError( """Top level struct elements require a name: %s"""%( element, ))
        # now create/update our instance class
        if named.has_key( 'instance_class' ):
            instance_class = named['instance_class']
            instance_class._struct = self
        else:
            namespace = {
                '_struct': self,
            }
            instance_class = type( 
                '%s_instance'%(self.name or 'struct' ),
                (StructInstance,),
                namespace,
            )
        for element in self.elements:
            setattr( 
                instance_class, element.name, 
                getattr( element, 'default', None)
            )
        self.instance_class = instance_class
    def __call__( self, **named ):
        return self.instance_class( **named )
    def __repr__( self ):
        elements = ", ".join([repr(x) for x in self.elements])
        if getattr( self, 'name',None ):
            return '%s( %s, name=%r )'%(
                self.__class__.__name__,
                elements,
                self.name,
            )
        else:
            return '%s( %s )'%(
                self.__class__.__name__,
                elements
            )
    def encode( self, target ):
        try:
            result = [
                element.encode( fragment )
                for element,fragment in target.iteritems()
            ]
        except (TypeError,ValueError,struct.error), err:
            err.args += (self,)
            raise
        else:
            return "".join( result )
    def decode( self, value, offset=0,target=None):
        """Decode this struct from the given string value"""
        result = self.instance_class()
        new = offset
        try:
            for element in self.elements:
                element_value,new = element.decode( value, new )
                setattr( result, element.name, element_value )
        except (TypeError,ValueError,struct.error), err:
            err.args += (self,)
            raise
        return result, new
Structure = Struct

class Element( object ):
    def __init__( self, **named ):
        if named.has_key( 'name' ):
            self.name = named.get( 'name','')
        if named.has_key( 'default' ):
            self.default = named['default']
    def __repr__( self ):
        if hasattr( self, 'name' ):
            return '%s( name=%r )'%(
                self.__class__.__name__, self.name,
            )
        else:
            return '%s( )'%(
                self.__class__.__name__,
            )
            
class SimpleElement( Element ):
    def encode( self, value ):
        try:
            return struct.pack( self.format, value )
        except (TypeError,ValueError,struct.error), err:
            err.args += (self.format,value,self)
            raise
    def decode( self, value, offset=0 ):
        new = offset + self.format_size
        try:
            return struct.unpack( self.format, value[offset:new] )[0], new 
        except (TypeError,ValueError,struct.error), err:
            err.args += (self.format,value[offset:new],self)
            raise

class Byte( SimpleElement ):
    format = '>b'
    format_size = struct.calcsize( format )
    max_value = 2**7-1
    min_value = -(2**7)
class UByte( SimpleElement ):
    format = '>B'
    format_size = struct.calcsize( format )
    max_value = 2**8-1
    min_value = 0
    # speeds us up ever-so-slightly...
    def encode( self, value ):
        return chr(value)
    def decode( self, value, offset=0 ):
        new = offset+1
        return ord(value[offset:new]),new
class Short( SimpleElement ):
    format = '>h'
    format_size = struct.calcsize( format )
    max_value = 2**15-1
    min_value = -(2**15)
class UShort( SimpleElement ):
    format = '>H'
    format_size = struct.calcsize( format )
    max_value = 2**16-1
    min_value = 0
# This is slower than struct module packing
#	def encode( self, value ):
#		return chr((value&0xff00)>>8)+chr(value&255)
class UInteger( SimpleElement ):
    """Unsigned 32-bit integer
    
    Converts to/from Long with bit-masks
    """
    format = '>I'
    format_size = struct.calcsize( format )
    max_value = 2**32-1
    min_value = 0
    def encode( self, value ):
        return super(UInteger,self).encode( value & 0xffffffffL )
    def decode( self, value, offset=0 ):
        value, new = super(UInteger,self).decode( value, offset )
        return value & 0xffffffffL, new
UInt = UInteger
class Integer( SimpleElement ):
    format = '>i'
    format_size = struct.calcsize( format )
    max_value = 2**31-1
    min_value = -(2**31)
Int = Integer
class ShortFloat( SimpleElement ):
    format = '>f'
    format_size = struct.calcsize( format )
class Float( SimpleElement ): # what Python people think of as a "float" is a double
    format = '>d'
    format_size = struct.calcsize( format )

class ListOf( Element ):
    def __init__( self, base_element,size_element=UByte(), **named ):
        super(ListOf,self).__init__( **named )
        self.size_element = size_element
        self.base_element = base_element
    def encode( self, value ):
        length = len(value)
        result = []
        result.append( self.size_element.encode( len(value) ) )
        for item in value:
            result.append( self.base_element.encode( item ))
        return "".join( result )
    def decode( self, value, offset=0 ):
        count,new = self.size_element.decode( value, offset )
        result = []
        for i in range( count ):
            item,new = self.base_element.decode( value, new )
            result.append( item )
        return result,new
class String( Element ):
    def __init__( self, size_element=UShort(), **named):
        super(String,self).__init__( **named )
        self.size_element = size_element
    def encode( self, value ):
        length = len(value)
        return self.size_element.encode( len(value) ) + value
    def decode( self, value, offset=0 ):
        count,start = self.size_element.decode( value, offset )
        new = start + count 
        result = value[start:new]
        return result, new

class Unicode( String ):
    def encode( self, value ):
        value = value.encode( 'utf-8' )
        return super( Unicode, self ).encode( value )
    def decode( self, value, offset=0 ):
        value, new = super(Unicode,self).decode( value, offset )
        return value.decode( 'utf-8' ), new

class Checksum( Element ):
    """Element which creates/checks checksum of client Element
    
    Intended normally to be used with larger packages such as
    ListOf( String()) as it's expensive in space...
    
    We have code in here to handle 32-bit crc functions that
    produce different results on 32-bit versus 64-bit platforms,
    we basically take a 0xffffffffL & on the number.
    
        Note: the check_element must *always* be unsigned as a 
        result of this!
    """
    def __init__( 
        self, client, 
        check_element=UInt(),check_function=zlib.adler32,
        **named
    ):
        if named.has_key( 'name' ):
            named.pop( 'name' )
        self.client = client
        self.check_element = check_element 
        self.check_function = check_function
        super( Checksum, self ).__init__( **named )
    def encode( self, value ):
        base = self.client.encode( value )
        checksum = self.check_function( base )
        return self.check_element.encode( checksum ) + base 
    def decode( self, value, offset=0 ):
        checksum,new = self.check_element.decode( value, offset )
        decoded,end = self.client.decode( value, new )
        new_checksum = self.check_function( value[new:end] ) & 0xffffffffL
        if checksum != new_checksum:
            raise ValueError( """Incoming checksum %s doesn't match %s"""%(
                new_checksum, checksum,
            ))
        return decoded, end 
    def get_name( self ):
        return self.client.name 
    def set_name( self, value ):
        self.client.name = value 
    name = property( get_name, set_name )
    
