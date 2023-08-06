"""Generates sequential ids"""
from qnet import locks

class IDGenerator( object ):
	"""Generates sequential IDs within a given range"""
	in_order = 0
	def __init__( self, max_id ):
		self.max_id = max_id
	def fix_in_order( self, id ):
		"""Fix in-order id to respect max message id"""
		base = id % self.max_id
		if base == 0:
			base = 1
		return base
	def set_in_order( self, id ):
		"""Set the next id in order"""
		self.in_order = id
		return self.in_order
	@locks.locked( )
	def next_in_order( self, set=False ):
		"""Assign a single id, returning the newly assigned id"""
		id = self.fix_in_order( self.in_order + 1 )
		if set:
			return self.set_in_order( id )
		return id

	def compare_in_order( self, current, new ):
		"""Compare new versus current with wrapping
		
		id is checked whether it is greater than 
		1/2 of total before/behind the current
		"""
		
		half = self.max_id // 2
		if new + self.max_id < current + half:
			return -1
		elif current + self.max_id < new + half:
			return 1
		else:
			return cmp( current, new )
