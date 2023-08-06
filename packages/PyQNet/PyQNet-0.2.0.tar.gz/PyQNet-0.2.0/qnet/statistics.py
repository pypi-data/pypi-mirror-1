"""Statistics gathering class for a network"""
import collections

class Statistics( object ):
	"""Collects messages for statistics gathering/adaptation"""
	CURRENT_WINDOW = 100
	total_count = 0
	total_bytes = 0
	total_duration = 0
	total_retries = 0
	package_count = 0
	package_bytes = 0
	package_duration = 0
	def __init__( self ):
		self._ack_wait_times = []
	def add_package( self, package ):
		"""Add a package that was sent"""
		self.package_count += 1
		self.package_bytes += package.length
		delta_time = package.time_ack-package.time_sent
		self.package_duration += delta_time
		self._ack_wait_times.append( delta_time )
		del self._ack_wait_times[:-self.CURRENT_WINDOW]
	def add_message( self, message ):
		"""Add message for calculations"""
		assert message.stats.time_sent 
		assert message.stats.time_ack
		self.total_count += 1
		self.total_retries += message.stats.count_sent
		self.total_duration += message.stats.time_ack-message.stats.time_sent
		self.total_bytes += message.stats.length 
	def ack_wait_time( self ):
		"""Calculate the period in which most messages have already responded
		
		This will obviously require tweaking, as we don't track which iteration the 
		other side responded to, so we don't know whether it was the last or the 
		first send that was replied to.
		"""
		base = self._ack_wait_time()
		return min((base,.05))
	def _ack_wait_time( self ):
		set = self._ack_wait_times[:]
		set.sort()
		fraction_index = len(set)//2
		most_set = set[fraction_index:]
		if most_set:
			return most_set[0]
		elif set:
			return set[-1]
		else:
			return 0.00
	
	def average_message_size( self ):
		if self.total_count:
			return self.total_bytes/float(self.total_count)
		return 0
	average_message_size = property( average_message_size )
	def average_message_duration( self ):
		if self.total_count:
			return self.total_duration/float(self.total_count)
		return 0
	average_message_duration = property( average_message_duration )
	def average_message_retries( self ):
		if self.total_count:
			return self.total_retries/float(self.total_count)
		return 0
	average_message_retries = property( average_message_retries )
	def average_package_size( self ):
		if self.package_count:
			return self.package_bytes/float(self.package_count)
		return 0
	average_package_size = property( average_package_size )
	def average_package_duration( self ):
		if self.package_count:
			return self.package_duration/float(self.package_count)
		return 0
	average_package_duration = property( average_package_duration )
	
	def display( self ):
		print """Statistics:
	Messages:
		total count: %s
		total bytes: %s
		average bytes: %s
		average duration: %s
		average retries: %s
	Packages:
		total count: %s
		total bytes: %s
		average bytes: %s
		average duration: %s
		"""%(
			self.total_count,
			self.total_bytes,
			self.average_message_size,
			self.average_message_duration,
			self.average_message_retries,
			
			self.package_count,
			self.package_bytes,
			self.average_package_size,
			self.average_package_duration,
		)
