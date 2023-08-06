"""Support for stateless message channel (full-state updates)"""
from qnet import messageset, locks
import weakref
import logging 
log = logging.getLogger( 'qnet.stateless' )
#log.setLevel( logging.DEBUG )

class KeyedQueue( object ):
	"""Maintains at most one element for each stateless_key in queue"""
	def __init__( self, set ):
		self.map = {}
		self.set = weakref.proxy(set)
	def __nonzero__( self ):
		return bool( self.map )
	@locks.locked( locks.NET_LOCK )
	def append( self, message ):
		"""Append this message to the queue"""
		key = message.stateless_key
		try:
			current = self.map.pop( key )
		except KeyError, err:
			pass
		else:
			log.info( 'Dropping un-sent message: %s', current )
			current.time_dropped = self.set.channel.timestamp()
			self.set.retire_message( current )
		self.map[ key ] = message 
	def insert( self, index, message ):
		return self.append( message )
	@locks.locked( locks.NET_LOCK )
	def pop( self, index ):
		return self.map.popitem()[1]
	def has_key( self, key ):
		return self.map.has_key( key )

class OutgoingSet( messageset.BaseOutgoingSet ):
	"""Delivers updates that supercede previous messages
	
	Stateless channels allow you to send messages which are 
	"compressed" such that we only ever send the latest
	known version of the message to the other side for a given 
	stateless "key".
	
	"""
	def __init__( self, *args, **named ):
		super(OutgoingSet,self).__init__( *args, **named )
		self.queue = KeyedQueue( self )
	def max_keys( self, ack_set ):
		"""Determine max id for each key-set"""
		key_sets = {}
		for id,message in ack_set.items():
			current = key_sets.get( message.stateless_key, None)
			if current is not None:
				if self.ids.compare_in_order( current, id ) in (-1,0):
					current = id 
			else:
				current = id 
			key_sets[message.stateless_key] = current
		return key_sets
	def process_acks( self, acks ):
		"""Process incoming acks to remove duplicate messages"""
		log.info( 'process_acks: %s', acks )
		ack_set = super( OutgoingSet, self ).process_acks( acks )
		if ack_set:
			log.debug( 'ack set: %s', ack_set )
			time_dropped = self.channel.timestamp()
			key_sets = self.max_keys( ack_set )
			log.debug( 'Key sets: %s', key_sets )
			to_pop = []
			try:
				for i,message in enumerate(self.sent_queue):
					last = key_sets.get( message.stateless_key )
					if last is not None:
						log.debug( 'Max %s for key %s', last, message.stateless_key )
						if self.ids.compare_in_order( message.id, last) in (0,-1):
							log.info( 'Dropping message %s', message )
							message.stats.time_dropped = time_dropped
							self.retire_message( message )
							to_pop.append( i )
			finally:
				# clean up that which needs to be removed
				to_pop.reverse()
				for pop in to_pop:
					self.sent_queue.pop( pop )
			log.debug( 'After acks sent queue: %s', self.sent_queue )
		return ack_set
	def add_resends( self, package,send_time ):
		"""Add resend messages to the package
		
		return whether we've completed resending of all resends
		"""
		wait_period = self.ack_wait_period()
		
		to_pop = []
		try:
			for i,message in enumerate( self.sent_queue ):
				if (
					message.stats.time_last_sent and 
					(message.stats.time_last_sent + wait_period) > send_time
				):
					continue
				else:
					if self.queue.has_key( message.stateless_key ):
						# we've got a newer version to go out...
						message.stats.time_dropped = send_time
						self.retire_message( message )
						to_pop.append( i )
					else:
						if not package.append( message ):
							return False
		finally:
			# clean up that which needs to be removed
			to_pop.reverse()
			for pop in to_pop:
				self.sent_queue.pop( pop )
		return True

class IncomingSet( messageset.BaseIncomingSet ):
	"""Incoming set that discards lower-numbered messages instead of retrying"""
	def __init__( self, *args, **named ):
		super(IncomingSet,self).__init__( *args, **named )
		self.max_seen = {}
	def process( self, incoming ):
		"""Process incoming messages from the network"""
		super( IncomingSet, self ).process( incoming )
		next = self.ids.next_in_order( )
		for message in incoming:
			last = self.max_seen.get( message.stateless_key )
			if last is not None:
				if self.ids.compare_in_order( last, message.id ) in (0,-1):
					self.retire_message( message )
					self.max_seen[ message.stateless_key ] = message.id
				else:
					log.info( 'Discarding stale message: %s', message )
