"""Channel-level message"""
from qnet.structure import *
import zlib

class MessageStats( object ):
    time_sent = None
    time_ack = None
    time_dropped = None
    time_last_sent = None # last time sent across network
    count_sent = 0
    length = 0 # encoded length

class Message( StructInstance ):
    """Individual message to another single point on the network"""
    MESSAGE_CONTINUED_TYPE = 1
    OVERHEAD = 2+2+2
    message_format = None
    def __init__( self, *args, **named ):
        """Initialize the message"""
        self.__dict__['stats'] = MessageStats()
        super(Message,self).__init__( 
            *args, **named 
        )
default_message_format = Struct(
    UShort( name='id' ),
    UShort( name='type', default=0 ),
    String( name='payload' ),
    instance_class = Message 
)
Message.message_format = default_message_format

class StatelessMessage( Message ):
    """Stateless-message sub-class which has stateless_key value"""
    OVERHEAD = 2+2+2+2
stateless_message_format = Structure(
    UShort( name='id' ),
    UShort( name='type', default=0 ),
    UShort( name='stateless_key',default=0 ),
    String( name='payload' ),
    instance_class = StatelessMessage,
)
StatelessMessage.message_format = stateless_message_format
