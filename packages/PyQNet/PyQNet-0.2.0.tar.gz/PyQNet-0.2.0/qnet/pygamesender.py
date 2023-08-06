"""Pygame-specific implementation details"""
import pygame
import pygame.event
from qnet import sender

class PygameSender( sender.Sender ):
	#EVENT_TYPE = pygame.USER_EVENT
	def send_event( self, code, **named ):
		"""Send event to the Pygame event queue"""
		named['code'] = code
		event = pygame.event.Event(
			self.EVENT_TYPE,
			**named 
		)
		pygame.event.post( event )
		return event 

