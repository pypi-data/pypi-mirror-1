"""Package of messages to send across the network connection"""
import logging 
log = logging.getLogger( 'qnet.package' )
#from message import Message
from qnet.structure import *
import zlib

ack_format = UByte( name='ack' )
package_format = Structure(
	UByte( name='channel', default = 0),
	UByte( name='id' ),
	ListOf( ack_format, name='acks' ),
	Checksum(
		ListOf( String( ), name='messages')
	),
)


class Package( list ):
	"""A package to send across the network
	
	This could as easily be called a bundle or a packet or any number of other 
	names, it's basically a collection of things that will be sent together.
	
	Note that Package's format is static, it must be the
	same regardless of the channel so that it can encode
	the channel information within it...
	"""
	length = 0
	id = None
	channel=0
	time_sent = None
	time_ack = None
	acks = None
	MAX_PACKET_SIZE = 1300
	def __new__( cls, time_stamp, *values ):
		"""Construct a new package, append each value in values"""
		base = super(Package,cls ).__new__(cls)
		base.__init__( time_stamp, *values )
		return base
	def __init__( self, time_stamp, *values ):
		self.acks = []
		self.messages = []
		self.time_stamp = time_stamp
		for value in values:
			self.append( value )
		
	def append_ack( self,message ):
		"""Add a message to ack to the other side"""
		if message not in self.acks:
			self.length += ack_format.format_size
			self.acks.append( message )
	def encode( self ):
		"""Encode to send across the network"""
		value = package_format(
			channel = self.channel,
			id = self.id,
			acks = [package.id for package in self.acks],
			messages = self,
		)
		return value.encode()
	def decode( cls, payload ):
		"""Decodes the payload as a set of acks and messages"""
		struct, next = package_format.decode( payload )
		messages = IncomingPackage()
		messages.set_channel( struct.channel )
		messages.set_id( struct.id )
		return struct.acks, messages, struct.messages
	decode = classmethod( decode )
	
	def append( self, message ):
		"""Append the given message to this package
		
		Updates message meta-data
		
		returns boolean indicating whether we added the message 
		"""
		payload = message.encode()
		message.stats.length = len(payload)
		if message.stats.length + self.length > self.MAX_PACKET_SIZE:
			return False
		else:
			message.stats.time_last_sent = self.time_stamp
			message.stats.count_sent += 1
			self.messages.append( message )
			
			super(Package,self).append( payload )
			self.length += message.stats.length
			return True

class IncomingPackage( list ):
	id = None 
	channel = 0
	def set_id( self, id ):
		self.id = id
	def set_channel( self, id ):
		self.channel = id 
	
	def decode( self, payloads, message_class ):
		for payload in payloads:
			message,next = message_class.decode( payload )
			#assert next == len(payload)
			self.append( message )
