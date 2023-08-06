"""Callback-registration-based sender for qnet"""
from qnet import sender
import logging 
log = logging.getLogger( 'qnet.sender.callback' )
import traceback
import Queue

class CallbackSender( sender.Sender ):
    """Callback-calling sending class for qnet 
    """
    LOG_UNHANDLED = False
    def __init__( self, *args, **named ):
        super( CallbackSender, self ).__init__( *args, **named )
        self.callbacks = {}
        self.message_callbacks = {}
        self.add_callback( 'message', self.default_message_callback )
    def default_message_callback( self, message,channel, **named ):
        type = message.type 
        callback = self.message_callbacks.get( type )
        if callback is not None:
            try:
                callback( message=message, channel=channel )
            except Exception, err:
                log.error(
                    """Exception during %r for type %r: %s""",
                    callback,
                    type,
                    traceback.format_exc(),
                )
        elif self.LOG_UNHANDLED:
            log.warn( """Unhandled event for message type: %s""", type )
    def add_message_callback( self, type, function ):
        """Registers callback for given message type
        
        type -- integer message type 
        function( **named ) where named has channel and message defined 
        """
        self.message_callbacks[type] = function 
    def add_callback( self, code, function ):
        """Registers callback for given code 
        
        code -- value from sender.codes to handle
        function -- callback function to register, will receive
            just the named arguments for the event, normally
            just channel and/or message.  See superclass functions 
            for the parameters involved...
        """
        if hasattr( code, 'code' ):
            code = code.code
        elif isinstance( code, str ):
            code = getattr( sender.Sender, code )
            if hasattr(code,'code'):
                code = code.code
        self.callbacks[ code ] = function
    def send_event( self, code, **named ):
        """Send event to the Pygame event queue"""
        self._retire_event( code, named )
    def _retire_event( self, code, named ):
        """Retire an event from our queue"""
        callback = self.callbacks.get( code )
        if callback is not None:
            try:
                callback( **named )
            except Exception, err:
                log.error(
                    """Exception during %r for code %r: %s""",
                    callback,
                    code,
                    traceback.format_exc(),
                )
        elif self.LOG_UNHANDLED:
            log.warn( """Unhandled event for: %r""", code )

class Server( object ):
    """Simple sample server object"""
    def register( self, send ):
        for name in dir(self):
            if name.startswith( 'on_' ):
                SIGNAL = name[3:]
                send.add_callback(
                    getattr( sender.Sender, SIGNAL ),
                    getattr( self, name )
                )
    

if __name__ == "__main__":
    logging.basicConfig()
    from qnet import socketnetwork 
    import threading
    send = CallbackSender()
    send.LOG_UNHANDLED = True
    # one side
    net = socketnetwork.Network( address=('127.0.0.1',16023), sender = send )
    # the other
    other = socketnetwork.Network( address=('127.0.0.1',16024), sender = send )
    class MyServer( Server ):
        def on_connect( self, channel ):
            log.warn( """Got a connection: %s %s""", channel.id, channel.address )
        def on_message( self, channel, message ):
            log.warn( """Got a message: %s""", message.payload )
            value = int(message.payload)
            if value > 5:
                channel.close()
            else:
                channel.send( str(value+1))
        def on_disconnect( self, channel):
            log.warn( """Channel disconnected: %s""", channel.id )
#            net.close()
#            channel.statistics.display()
    server = MyServer()
    server.register( send )
    channel = net.channel( other.bind_address )
    channel.send( str(1) )
    t = threading.Thread( target = other.loop_forever )
    t.daemon = True
    t.start()
    net.loop_until_finished()
    
