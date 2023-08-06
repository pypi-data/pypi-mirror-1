"""Incoming/outgoing message-sets for channels"""
from qnet import locks, idgenerator
from qnet.package import Package
import logging 
log = logging.getLogger( 'qnet.messageset' )
#log.setLevel( logging.DEBUG )

class MessageSet( object ):
	"""Base class for tracking of ordered message-sets (manages pending IDs)"""
	channel = None
	queue = None
	def __init__( self, channel=None ):
		"""Initialize the storage including the internal queue (list)"""
		self.channel = channel
		self.queue = []
		self.ids = idgenerator.IDGenerator( 
			self.channel.protocol.MAX_MESSAGE_ID 
		)
	def retire_message( self, message ):
		"""Retire this message, either by adding to queue or sending message"""

class BaseIncomingSet( MessageSet ):
	"""Base class for incoming message-sets"""
	def process( self, incoming ):
		"""Process incoming messages from the network"""
		# note that we ack ASAP so that we don't resend ooo messages 
		# if they've already been received...
		self.channel.outgoing.send_ack( incoming )
	def has_pending( self ):
		return len(self.queue)
	def get( self ):
		"""Get all fully-received messages from the queue"""
		result = []
		while self.queue:
			result.append( self.queue.pop(0))
		return result
	def retire_message( self, message ):
		"""Retire this message, either by adding to queue or sending message"""
#		log.info( 'Retiring incoming message: %s', message )
		if self.channel.sender:
			self.channel.sender.message( self.channel, message )
		else:
			self.queue.append( message )
		

class BaseOutgoingSet( MessageSet ):
	"""Base class for outgoing message-sets"""
	pending_acks = None
	failures = 0
	def __init__( self, channel=None ):
		super(BaseOutgoingSet,self).__init__( channel )
		self.pending_acks = []
		self.sent_queue = []
		self.in_flight_packages = {}
		self.package_ids = idgenerator.IDGenerator( 
			self.channel.protocol.MAX_PACKAGE_ID 
		)
	def send( self, message ):
		"""Send this message on our channel"""
		message.id = self.ids.next_in_order( set=True )
		message.stats.time_sent = self.channel.timestamp()
		self.queue.append( message )
		# XXX check for queue length/duration here, throw error if too long
		return message
	def send_ack( self, package ):
		"""Send an ack message for this (incoming) message"""
		#print 'send ack', message.id
		if len(package):
			# only ack messages, not pure-ack
			self.pending_acks.append( package )
#			print 'should send ack for', package.id
			assert self.has_pending()
	def send_package( self, package ):
		"""Send this package out across the network"""
		if package.length:
			package.id = self.package_ids.next_in_order( set = True )
			log.info( 'Sending package #%s with %s messages and %s acks', package.id, len(package),len(package.acks))
			package.channel = self.channel.id
			package.time_sent = self.channel.timestamp()
			#print 'sending', package
			# do we expect an ack?
			if len(package):
				log.info( 'Adding to in_flight packages: %s', package.id )
				self.in_flight_packages[ package.id ] = package
#			else:
#				print 'ack-only', [x.id for x in package.acks]
			self.channel.send_raw( package.encode() )
#		else:
#			print 'null package being sent'
	_current_ack_wait = None
	_last_ack_time = 0 # last time we were acked
	_current_ack_wait_count = 0
	def ack_wait_period( self ):
		"""Calculate a reasonable acknowledgement wait period (period before retry)"""
		# TODO better reset period calculation...
		current_count = self.channel.statistics.package_count
		if (
			self._current_ack_wait is None or 
			current_count > self._current_ack_wait_count + 100
		):
			self._current_ack_wait = wait = self.channel.statistics.ack_wait_time()
			self._current_ack_wait_count = current_count
			if wait > self.channel.protocol.CONGESTION_PERIOD:
				if self.channel.sender:
					self.channel.sender.congestion_warning( self.channel )
				log.warn( """Mean round-trip for channel %s is %0.5f"""%(
					self.channel,wait,
				))
#			log.debug( 'Ack wait period recalculated: %s', self._current_ack_wait )
		return self._current_ack_wait
	
	def has_pending( self ):
		"""Do we have processing to do?"""
		return (
			(self.pending_acks or self.queue or self.sent_queue)
			and self.channel.active
		)
	def filter_in_flight( self, send_time ):
		"""Filter any in-flight messages based on send_time"""
		old_date = send_time - max((
			(self.ack_wait_period() * 2),
			self.channel.protocol.PACKAGE_EXPIRE,
		))
		congestion_time = send_time - self.channel.protocol.CONGESTION_PERIOD
		congestion_count_max = self.channel.protocol.CONGESTION_COUNT
		max_failures = self.channel.protocol.MAX_FAILURES
		max_in_flight = self.channel.protocol.MAX_IN_FLIGHT
		
		if (
			# in-flight climbing up
			len(self.in_flight_packages) > congestion_count_max or 
			# haven't seen an ack in a while...
			self._last_ack_time < congestion_time
		):
			# only check if/when we're beginning to run out...
			# note: we will often show up here with all old discarded
			# values, so we only count ones since our last ack as failures
			congestion_count = 0
			in_flight = self.in_flight_packages.items()
			for key,package in in_flight:
				package_time = package.time_sent
				if package_time < self._last_ack_time:
					# stale
					try:
						self.in_flight_packages.pop( key )
					except KeyError, err:
						pass 
				elif package.time_sent < old_date:
					# expiring
					try:
						del self.in_flight_packages[ key ]
					except KeyError, err:
						# something already retired this package...
						pass
					else:
						self.failures += 1
						if self.failures > max_failures:
							log.warn( 'Closing channel %s due to apparent network connection loss', self.channel )
							if self.channel.sender:
								self.channel.sender.congestion_critical( self )
							if self.channel.protocol.CLOSE_ON_MAX_FAILURES:
								self.channel.close()
				elif package_time < congestion_time:
					congestion_count += 1
			if (
				congestion_count >= congestion_count_max
			):
				log.info( 
					"Network congestion detected: %s", 
					len(self.in_flight_packages)
				)
				# XXX Altering our behaviour in this case would be useful...
				if self.channel.sender:
					self.channel.sender.congestion_warning( self.channel )
			if len(self.in_flight_packages) >= max_in_flight:
				log.info( "%s packages in flight, unable to continue sending", len(self.in_flight_packages))
				return False
		return True 
	def add_acks( self, package ):
		"""Add acks to the given package up to package size-limit
		
		return whether we've completed processing of all pending acks
		"""
		max_size = self.channel.protocol.MAX_PACKET_SIZE
		ack_size = self.channel.protocol.ack_format.format_size
		max_acks = self.channel.protocol.ack_format.max_value
		count = 0
		while self.pending_acks:
			if len(package) < (max_size-ack_size) and len(package.acks) < max_acks:
				try:
					package.append_ack( self.pending_acks.pop(0) ) # message-like ack package 
				except IndexError, err:
					pass
			else:
				return False
		return True
	def add_resends( self, package,send_time ):
		"""Add resend messages to the package
		
		return whether we've completed resending of all resends
		"""
		wait_period = self.ack_wait_period()
		stale_time = send_time - wait_period
#		log.debug( 'stale time: %s', stale_time )
		for message in self.sent_queue:
			if (
				message.stats.time_last_sent >= stale_time
			):
				continue
			else:
#				log.warn(
#					'Resending with period of %s', 
#					send_time - message.stats.time_last_sent
#				)
				if not package.append( message ):
					return False
		return True
	def add_queued( self, package, send_time ):
		max_size = self.channel.protocol.MAX_PACKET_SIZE
		while self.queue:
			try:
				message = self.queue.pop( 0 )
			except IndexError, err:
				pass 
			else:
				if package.append( message ):
					assert message.stats.length < max_size, """Attempting to send a %r byte payload, maximum payload size is %s:\n%r"""%(
						message.stats.length, max_size,
						payload[:80]
					)
					self.sent_queue.append( message )
				else:
					self.queue.insert( 0, message )
					return False
		return True
	def build_ack_set( self, acks ):
		"""Build set of messages which have been acked by package acks"""
		time_ack = self.channel.timestamp()
		ack_set = {}
		for ack in acks:
			try:
				package = self.in_flight_packages.pop( ack )
			except KeyError, err:
				log.info( 'Not currently in flight %s', ack )
			else:
				log.debug( 'Acked: %s %s', ack, len(package) )
				package.time_ack = time_ack
				self.channel.statistics.add_package( package )
				for message in package.messages:
					ack_set[message.id] = message
		return ack_set
	def retire_message( self, message ):
		"""Retire this message, either by adding to queue or sending message"""
#		log.info( 'Retiring outgoing message: %s', message )
		if message.stats.time_ack:
			self.channel.statistics.add_message( message )
			if self.channel.sender:
				self.channel.sender.message_acked( self.channel, message )
			# no other notice for this "event"
		else:
			if self.channel.sender:
				self.channel.sender.message_dropped( self.channel, message )
			# no other notice for this "event"
	def process_acks( self, acks ):
		"""Process acknowledgement of message receipt from other side
		
		This handles explicitly-acked messages only
		"""
		self.failures = 0
		time_ack = self.channel.timestamp()
		self._last_ack_time = time_ack
		ack_set = self.build_ack_set( acks )
		if ack_set:
			set = []
			for message in self.sent_queue:
				if ack_set.has_key( message.id ):
					message.stats.time_ack = time_ack
					self.retire_message( message )
					ack_set[ message.id ] = message
				else:
					set.append( message )
			self.sent_queue = set
		return ack_set

	def process( self ):
		"""Process all pending messages (send all pending messages incl. acks)"""
		# clear out old packages...
		send_time = self.channel.timestamp()
		if not self.filter_in_flight( send_time ):
			# too many in flight...
			log.info( """Too many in flight, not sending""" )
			return False
		# check to see if there's anything to do...
		if not self.has_pending():
			log.info( """Nothing pending, not sending""" )
			return False 
		# localize vars for this run...
		# okay, may have something to do...
		# pack a package (or packages) to send to the other side
		package = Package( send_time )
		sent = 0
		while not self.add_acks( package ):
			self.send_package( package )
#			log.info( 'new package for acks' )
			package = Package( send_time )
			sent += 1
		while not self.add_resends( package, send_time ):
			self.send_package( package )
#			log.info( 'new package for resends' )
			package = Package( send_time )
			sent += 1
		while not self.add_queued( package, send_time ):
#			log.info( 'new package for queued' )
			break
		if package.length:
			self.send_package( package )
			sent += 1
		return sent
