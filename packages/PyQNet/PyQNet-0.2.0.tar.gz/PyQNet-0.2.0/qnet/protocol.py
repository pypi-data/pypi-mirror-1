"""Base protocol definitions (the qnet-level structures and parameters)"""
from qnet.structure import *
from qnet import message, package

class Protocol( object ):
	"""Defines constants for communication parameters"""
	# this is a static "magic" value
	MAX_PACKET_SIZE = 1300  # 1400 minus overhead for bookkeeping stuff
	
	# these are tweakable optimization elements
	PACKAGE_EXPIRE = 1.00 # window for acks (minimum, will grow on slow networks)
	MAX_IN_FLIGHT = 64 # maximum packages in-flight at any given time
	MAX_FAILURES = 32 # maximum number of sequential failures (time before disconnect)
	CONGESTION_PERIOD = 0.05 # warn users if round-trip goes above this
	CONGESTION_COUNT = 8 # for this many messages
	
	# this is an option
	CLOSE_ON_MAX_FAILURES = True
	
	# this is functional operation stuff
	message_class = message.Message
	message_format = message_class._struct

	# these two formats are basically static...
	ack_format = package.ack_format
	package_format = package.package_format
	
	# these three should come from the structures
	MAX_PACKAGE_ID = package_format.id.max_value 
	MAX_MESSAGE_ID = message_format.id.max_value

RELIABLE_PROTOCOL = Protocol()

class StatelessProtocol( Protocol ):
	"""Stateless channel protocol (uses stateless message)"""
	message_class = message.StatelessMessage
	message_format = message_class._struct
	
	MAX_MESSAGE_ID = message_format.id.max_value
	MAX_STATELESS_KEY = message_format.stateless_key.max_value

STATELESS_PROTOCOL = StatelessProtocol()
