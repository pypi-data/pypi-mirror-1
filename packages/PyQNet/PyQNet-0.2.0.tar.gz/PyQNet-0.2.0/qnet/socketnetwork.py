"""Raw UDP blocking socket implementation of network transport"""
from qnet import network
import socket,errno, select, time
import logging 
log = logging.getLogger( 'qnet.network.socket' )
#log.setLevel( logging.DEBUG )

class Network( network.Network ):
    """Non-blocking socket-based network implementation
    
    Defaults to communicating on all interfaces on port 16023
    """
    socket = None
    closed = False
    # EXTERNAL API
    def close( self ):
        """Close down this network (e.g. close our sockets)
        
        This is part of the public API
        """
        super( Network,self ).close()
        if self.socket:
            socket = self.socket
            self.wake()
            log.info( 'Closing socket: %s', self.address )
            if socket:
                socket.close()
            self.socket = None
    # INTERNAL API
    def open( self ):
        """Perform initial network initialization (e.g. create/open a socket)
        
        This is an internal function and should not be called by user code
        """
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setblocking( False )
            address = self.bind_address
            self.address = address
            log.info( 'local socket bind address: %s', address)
            self.socket.bind( address )
            log.debug( 'finished open' )
    def wake( self ):
        """Wake up the network with a null message"""
    def send_raw( self, address, payload ):
        """Send payload to address via socket write"""
        if not self.socket:
            self.open()
        try:
            FLAGS = 0
            self.socket.sendto( payload, FLAGS, address )
        except socket.error, err:
            if err[0] == errno.EWOULDBLOCK:
                pass 
            elif err[0] == errno.EBADF:
                if not self.closed:
                    log.warn( "Bad socket in sendto call, resetting socket: %s", self.socket )
                    self.socket = None
            else:
                raise
    def receive_all( self ):
        """Receive all pending messages from the low-level network queue"""
        if not self.socket:
            self.open()
        set = []
        while True:
            try:
                set.append( self.socket.recvfrom( 2048 ))
            except socket.error, err:
                if err[0] == errno.EWOULDBLOCK:
                    return set
                else:
                    raise
        return set
    def readable( self, timeout=0.0 ):
        """Are we network readable?"""
        if not self.socket:
            self.open()
        read,write,excepts = select.select( 
            [self.socket],[],[],timeout 
        )
        return bool(read)
        
    def wait( self, timeout=0.05, repeat=20 ):
        """Wait until there is network activity, or timeout occurs"""
        readable = False 
        while not readable:
            # this loop allows us to exit on signals and the like...
            repeat -= 1
            readable = self.readable(timeout)
            if (repeat < 0) and not readable:
                return False
        return True 
    
