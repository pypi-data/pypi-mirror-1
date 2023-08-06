
class Code( int ):
	def __new__( cls, code, name ):
		base = super( Code,cls).__new__( cls, code )
		base.name = name 
		return base
	def __repr__( self ):
		return self.name
code_names = """CONNECT
DISCONNECT
CONGESTION_WARNING
CONGESTION_CRITICAL
MESSAGE
MESSAGE_ACKED
MESSAGE_DROPPED""".split()
codes = [
	Code( i+1, name) 
	for (i,name) in enumerate( code_names ) 
]


class Sender( object ):
	"""Basic interface for sending messages regarding network events"""
	codes = codes
	def send_event( self, code, **named ):
		"""Send given event to the GUI system"""
		pass
	def connect( self, channel ):
		"""Send message that a channel has connected"""
		return self.send_event(
			self.CONNECT,
			channel = channel,
		)
	def congestion_warning( self, channel ):
		"""Send message that a channel has become congested"""
		return self.send_event(
			self.CONGESTION_WARNING,
			channel = channel,
		)
	def congestion_critical( self, channel ):
		"""Send message that a channel has become critically congested"""
		return self.send_event(
			self.CONGESTION_CRITICAL,
			channel = channel,
		)
	def disconnect( self, channel ):
		"""Send message that a channel has disconnected"""
		return self.send_event(
			self.DISCONNECT,
			channel = channel,
		)
	
	def message( self, channel, message ):
		"""Send message that a channel has received a message"""
		return self.send_event(
			self.MESSAGE,
			channel = channel,
			message = message,
		)
	def message_acked( self, channel, message ):
		"""Send message that a channel has received ack for a message"""
		return self.send_event(
			self.MESSAGE_ACKED,
			channel = channel,
			message = message,
		)
	def message_dropped( self, channel, message):
		"""Send message that a channel has dropped message in deference to another"""
		return self.send_event(
			self.MESSAGE_DROPPED,
			channel = channel,
			message = message,
		)
for code in codes:
	setattr( Sender, code.name, code )
	function = getattr(Sender,code.name.lower()).im_func
	setattr( function, 'code', code )
