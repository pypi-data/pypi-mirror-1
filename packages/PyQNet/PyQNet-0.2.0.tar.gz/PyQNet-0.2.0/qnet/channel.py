"""The channel object (network interface) for a connection to a given point"""
import struct
from qnet import message, messageset, statistics,protocol
from qnet.package import Package

class Channel( object ):
    """Channel of communications with another single point on the network"""
    network = None
    active = True
    def __init__( 
        self, address, id=0, 
        stateless=False, 
        local=True,
    ):
        """Init the connection
        
        address -- address to which to bind...
        id -- channel id (unique id to distinguish between channels)
        stateless -- whether every message is guaranteed to be delivered
        
            if True, will resend messages until they are received and 
            will delay delivery of messages received until all previous
            messages are received 
            
            if False, will only resend the last message sent and will 
            drop messages which are received out-of-order
        
        local -- whether this is a local channel (created by us, not a 
            remote connection)
        """
        self.address = address
        self.id = id
        self.stateless = stateless
        if stateless:
            self.protocol = protocol.STATELESS_PROTOCOL
            from qnet import stateless
            self.incoming = stateless.IncomingSet( self )
            self.outgoing = stateless.OutgoingSet( self )
        else:
            self.protocol = protocol.RELIABLE_PROTOCOL
            from qnet import reliable
            self.incoming = reliable.IncomingSet( self )
            self.outgoing = reliable.OutgoingSet( self )
        self.statistics = statistics.Statistics()
        self.local = local
    def close( self ):
        """Close this channel for further processing"""
        self.active = False 
        if self.network:
            self.network.detach( self )
            # send a close message for this channel...
    def __repr__( self ):
        return '%s( %r, id=%s, stateless=%s,local=%r )'%(
            self.__class__.__name__,
            self.address,
            self.id,
            self.stateless,
            self.local,
        )
    def split_large_message( self, payload, **named ):
        # create continued data-set...
        max_size = self.protocol.MAX_PACKET_SIZE - self.protocol.message_class.OVERHEAD - 4 # fudge factor...
        if len(payload) > max_size:
            if self.stateless:
                raise ValueError(
                    """Payload of %s bytes is too large for stateless delivery, max size is %s"""%( len(payload), max_size, ) 
                )
            while payload:
                current,payload = payload[:max_size],payload[max_size:]
                if payload:
                    # continued message 
                    yield self.protocol.message_class(
                        payload= current, type=1
                    )
                else:
                    yield self.protocol.message_class(
                        payload= current, **named
                    )
        else:
            yield self.protocol.message_class(
                payload= payload, **named
            )
    # external API
    def send( self, payload, **named ):
        """Send the given payload to the given address"""
        if named.get( 'type' ) == self.protocol.message_class.MESSAGE_CONTINUED_TYPE:
            raise ValueError( 
                """Message continued type (%s) cannot be directly specified"""%(
                    self.protocol.message_class.MESSAGE_CONTINUED_TYPE,
                )
            )
        if not self.active:
            return None
        try:
            if isinstance( payload, unicode ):
                payload = payload.encode( 'utf-8' )
            elif not isinstance( payload, str ):
                # structure types...
                payload = payload.encode()
            result = None
            for message in self.split_large_message( payload, **named ):
                result = self.outgoing.send( message )
            return message
        finally:
            self.network.wake()

    def get( self ):
        """Retrieve all incoming messages for this channel
        
        Note: normally you would use events sent by a sender 
        object, this kind of polling won't let you sleep!
        """
        return self.incoming.get()
    
    # internal API
    def key( self ):
        """Produce our unique key
        
        For now this is just the address
        """
        return self.address,self.id
    @classmethod
    def key_from_message( cls, address, package ):
        """Produce channel key from address/message pair"""
        return address,package.channel
    
    def set_network( self, network ):
        """Set our network connection for low-level operations"""
        self.network = network
        self.sender = network.sender
    
    def timestamp( self ):
        """Get current network timestamp"""
        return self.network.timestamp()
    
    def process_raw( self, acks, messages ):
        """Process incoming set of raw package payloads
        """
        self.outgoing.process_acks( acks )
        self.incoming.process( messages )
    
    def send_raw( self, payload ):
        """Send the raw packge payload one time to our target end-point"""
        if self.network:
            return self.network.send_raw( self.address, self.network.compress(payload) )
        else:
            log.error( """Attempt to send_raw before network set on channel""" )
            return False
    
    def pending( self ):
        """Do we have any pending operations"""
        return self.outgoing.has_pending() or self.incoming.has_pending()

class Group( object ):
    """A meta-channel for sending messages to more than one channel at once
    
    This is intended to be used by application-level code to manage
    channel-groups, it doesn't affect the network level at all, as the 
    messages just go out to the channels connected in the group
    """
    def __init__( self, name, channels=None ):
        """Initialize this group with the name we use as a key"""
        self.name = name 
        self.channels = {}
        if channels is not None:
            for channel in channels:
                current.add_channel( channel )
    def __repr__( self ):
        return '%s( %r, %r )'%(
            self.__class__.__name__,
            self.name,
            self.channels.values(),
        )
    def add_channel( self, channel ):
        """Set the channels which belong to this group"""
        key = channel.key()
        if not self.channels.has_key( key ):
            self.channels[ key ] = channel 
        return channel 
    def remove_channel( self, channel ):
        """Remove the channel from this group"""
        key = channel.key()
        try:
            del self.channels[ key ]
        except KeyError, err:
            return False 
        else:
            return True 

    def send( self, payload ):
        """Send this payload to all members of the group, return list of message objects
        
        TODO treat this like a single message wrt GUI-level events
        """
        result = []
        for channel in self.channels.values():
            result.append( channel.send( payload ))
        return result
    
