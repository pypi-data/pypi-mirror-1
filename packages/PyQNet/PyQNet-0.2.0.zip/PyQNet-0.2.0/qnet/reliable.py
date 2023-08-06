"""Support for ordered-reliable message sending (delta updates)"""
from qnet import messageset,locks
from qnet.package import Package
import logging 
log = logging.getLogger( 'qnet.reliable' )

class OutgoingSet( messageset.BaseOutgoingSet ):
    """Set of messages going out on a channel"""

class IncomingSet( messageset.BaseIncomingSet ):
    """Set of messages coming into a channel"""
    out_of_order = None
    def __init__( self, channel=None ):
        self.out_of_order = {}
        self.continued = ""
        super(IncomingSet,self).__init__( channel )
    def process( self, incoming ):
        """Process incoming messages from the network"""
        super( IncomingSet, self ).process( incoming )
        next = self.ids.next_in_order( )
        for message in incoming:
            if message.id == next:
                self.ids.next_in_order( set=True )
                if message.type == message.MESSAGE_CONTINUED_TYPE:
                    self.continued += message.payload 
                else:
                    if self.continued:
                        message.payload = self.continued + message.payload 
                        self.continued = ""
                    self.retire_message( message )
                next = self.pop_ooo()
            elif self.ids.compare_in_order( next, message.id ) == -1:
                self.insert_ooo( message )
    @locks.locked( )
    def pop_ooo( self ):
        """Pop all ooo messages into queue while in order"""
        next = self.ids.next_in_order(  )
        while self.out_of_order.has_key( next ):
            message = self.out_of_order.pop( next )
            if message.type == message.MESSAGE_CONTINUED_TYPE:
                self.continued += message.payload 
            else:
                if self.continued:
                    message.payload = self.continued + message.payload 
                    self.continued = ""
                self.retire_message( message )
            self.ids.next_in_order( set=True )
            next = self.ids.next_in_order(  )
        return next
    @locks.locked( )
    def insert_ooo( self, message ):
        """Insert an out-of-order message into our queue of such
        
        Must be locked during this procedure
        """
        self.out_of_order[message.id] = message
