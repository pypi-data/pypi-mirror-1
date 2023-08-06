"""Trivial UDP based networking library for Python games"""
import time
import logging 
import zlib
log = logging.getLogger( 'qnet.network' )
#log.setLevel( logging.DEBUG )
from qnet.channel import Channel, Group
from qnet.package import Package

class Network( object ):
    """Overall network running object (interface definition)
    """
    channels = None
    closed = False
    channel_id = 0
    address = None # our external address (AFAWK)
    def __init__( self, address=('',16023), sender=None, compression=zlib ):
        """Initialize the network connection with given configuration 
        """
        self.channels = {}
        self.blocks = {}
        self.groups = { '': Group('')}
        self.bind_address = address
        self.sender = sender
        self.open()
        self.compression = compression
    def open( self ):
        """Perform initial network initialization (e.g. create/open a socket)
        
        You don't normally have to call open
        """
    def close( self ):
        """Close down this network (e.g. close our sockets)
        
        You will likely want to call this during your game's shutdown operations
        """
        self.closed = True
        for id,channel in self.channels.items():
            self.detach( channel )

    def block( self, channel, block=True ):
        """Block (unblock) the given channel's address from connecting
        
        As we normally allow anyone to connect and create a channel, this method 
        allows you to see that someone isn't welcome and block the address
        """
        log.warn( 'Block %r = %r', channel.address, block )
        self.blocks[ channel.address ] = block
    
    def channel( self, address, id=0, **named):
        """Create and return a new channel to the given address"""
        named['local'] = True
        channel = Channel( address=address, id=id, **named )
        self.attach( channel )
        log.info( 'Local channel creation: %r', channel )
        return channel
    def wait_channel( self, address, id=0, **named ):
        """Configure channel for incoming messages from address/id"""
        named['local'] = False
        channel = Channel( address=address, id=id, **named )
        self.attach( channel )
        log.info( 'Waiting for channel: %r', channel )
        return channel
        
    def group( self, name, channels=None ):
        """Create/retrieve a group for interest monitoring
        
        name -- unique key for the group 
        
        returns the (potentially new) group
        """
        current = self.groups.get( name )
        if current is None:
            self.groups[ name ] = current = Group( name, channels )
        elif channels is not None:
            for channel in channels:
                current.add_channel( channel )
        return current 
    
    def pending( self ):
        """Do we have anything to do at the moment?
        
        This is a polling call to determine if there's anything left to do...
        """
        for channel in self.channels.values():
            if channel.pending():
                return True 
        if self.readable():
            return True 
        return False 
    # TODO: set a flag for this stuff rather than querying, channels 
    # that have no outgoing operations are known, so we could add/remove 
    # them to/from a core group...
    def loop_until_finished( self ):
        """Loop until we have nothing pending"""
        while self.pending():
            while self.main_loop():
                pass
            self.wait(timeout=0.05, repeat=2)
    def loop_forever( self ):
        """Server-style loop that waits on socket and dispatches messages"""
        while True:
            while self.main_loop():
                pass
            self.wait(timeout=0.05, repeat=2)
    def main_loop(self ):
        """Main loop which (asynchronously) processes network operations"""
        did_something = False
        raw_messages = self.receive_all()
        for message,address in raw_messages:
            if message:
                message = self.decompress( message )
                did_something = True
                acks,pack,payload = Package.decode( message )
                if pack is not None:
                    key = Channel.key_from_message( address,pack )
                    channel = self.channels.get( key )
                    if not channel and pack.channel is 0:
                        log.debug( 'New incoming 0 channel: %s', key )
                        channel = self.new_connection( address, pack )
                    if channel:
                        pack.decode( payload, channel.protocol.message_class )
                        channel.process_raw( acks,pack )
                    else:
                        log.warn( 
                            'Message received for undefined channel: %r, wait_channel( address, id ) was not called on server for this channel.', 
                            key
                        )
                else:
                    log.warn( 'Null package: %s', message )
        for channel in self.channels.values():
            if channel.outgoing.process():
                did_something = True 
        return did_something
    def new_connection( self, address, package):
        """New connection from somewhere asking to set up a channel
        
        The default implementation here just creates a new Channel for the given address
        and attaches it to us.  Higher-level interfaces will want to e.g. sent events or the 
        like.
        """
        log.info( 'New connection from: %r', address )
        if not self.blocks.get( address ):
            channel = Channel( address, local=False )
            self.attach( channel )
            return channel
        else:
            log.warn( """Rejected connection from %r (address is in the block-list)""", address )
            return None
    def attach( self, channel ):
        """Add the given channel to our set of channels to process"""
        self.channels[ channel.key() ] = channel 
        channel.set_network(self)
        self.group('').add_channel( channel )
        if self.sender:
            self.sender.connect( channel )
    def detach( self, channel, block=False ):
        """Detach this channel and optionally prevent reconnects"""
        if block:
            self.block( channel )
        if self.sender:
            self.sender.disconnect( channel )
        for group in self.groups.values():
            group.remove_channel( channel )
        try:
            del self.channels[ channel.key() ]
        except KeyError, err:
            return False
        else:
            return True
    def timestamp( self ):
        """Get current network timestamp"""
        return time.time()
    # sub-classes override these to provide network-level operations
    def wake( self ):
        """Wake up the network (if necessary)"""
    def send_raw( self, address, payload ):
        """Send raw packet to given address"""
    def receive_all( self ):
        """Receive all pending messages from the network
        
        retrieves set of message,address pairs
        """
        return []

    def compress( self, payload ):
        """Do any appropriate compression on payload"""
        if self.compression:
            payload = self.compression.compress( payload )
        return payload 
    def decompress( self, payload ):
        """Do any appropriate decompression on payload"""
        if self.compression:
            payload = self.compression.decompress( payload )
        return payload 
    
