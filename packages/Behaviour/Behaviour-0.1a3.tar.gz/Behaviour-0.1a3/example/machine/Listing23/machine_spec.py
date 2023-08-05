import behaviour
import unittest

import machine

class Machine( behaviour.Behaviour ):

	def setUp( self ):
	
		self.machine = machine.Machine( [ 'Shopping', 'CheckingOut' ] )
		self.machine.events = { 'CheckOut' : { 'from' : 'Shopping', 'to' : 'CheckingOut' } }

	def should_initially_have_state_of_the_first_state( self ):
	
		self.shouldEqual( self.machine.state, 'Shopping' )

	def should_remember_list_of_valid_states( self ):
	
		self.shouldEqual( self.machine.states, [ 'Shopping', 'CheckingOut' ] )
	
	def should_remember_list_of_events_with_transitions( self ):
	
		self.shouldEqual( self.machine.events, { 'CheckOut' : { 'from' : 'Shopping', 'to' : 'CheckingOut' } } )
		
	def should_transition_to_CheckingOut_upon_trigger_CheckOut_event( self ):
	
		self.machine.trigger( 'CheckOut' )
		self.shouldEqual( self.machine.state, 'CheckingOut' )
		
	def should_transition_to_Success_upon_trigger_AcceptCard( self ):
	
		self.machine.events = { 'CheckOut' : { 'from' : 'Shopping', 'to' : 'CheckingOut' },
								'AcceptCard' : { 'from' : 'CheckingOut', 'to' : 'Success' } }
		self.machine.trigger( 'CheckOut' )
		self.shouldEqual( self.machine.state, 'CheckingOut' )
		self.machine.trigger( 'AcceptCard' )
		self.shouldEqual( self.machine.state, 'Success' )
		
	def should_not_transition_from_Shopping_to_Success_upon_trigger_AcceptCard( self ):
	
		self.machine.events = { 'CheckOut' : { 'from' : 'Shopping', 'to' : 'CheckingOut' },
								'AcceptCard' : { 'from' : 'CheckingOut', 'to' : 'Success' } }
		self.machine.trigger( 'AcceptCard' )
		self.shouldNotEqual( self.machine.state, 'Success' )

if __name__ == '__main__':
	suite = []
	suite += unittest.TestLoader().loadTestsFromTestCase( machine_spec )
	alltests = unittest.TestSuite( suite )
	unittest.TextTestRunner( verbosity=2 ).run( alltests )