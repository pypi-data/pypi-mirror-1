"""Locks to provide thread-safety for qnet"""
import qnet
import threading 
NET_LOCK = threading.RLock()

def locked( lock = NET_LOCK ):
	"""Produces a version of function where lock is acquired/released around the call"""
	if qnet.THREADED:
		def _locked( function ):
			def with_lock( *args, **named ):
				lock.acquire()
				try:
					return function( *args, **named )
				finally:
					lock.release()
			with_lock.__name__ = function.__name__
			with_lock.__doc__ = function.__doc__
			with_lock.__dict__.update( function.__dict__ )
			return with_lock
	else:
		def _locked( function ):
			return function 
	return _locked
