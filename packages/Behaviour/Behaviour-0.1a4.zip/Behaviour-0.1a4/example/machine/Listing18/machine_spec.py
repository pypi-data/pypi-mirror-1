import behaviour
import unittest

import machine

class machine_spec( behaviour.Behaviour ):

	def setUp( self ):
	
		self.machine = machine.Machine( [ 'Shopping', 'CheckingOut' ] )
		self.machine.events = { 'CheckOut' : { 'from' : 'Shopping', 'to' : 'CheckingOut' } }

	def test_MachineShouldInitiallyHaveStateOfTheFirstState( self ):
	
		self.shouldEqual( self.machine.state, 'Shopping' )

	def test_MachineShouldRememberListOfValidStates( self ):
	
		self.shouldEqual( self.machine.states, [ 'Shopping', 'CheckingOut' ] )
	
	def test_MachineShouldRememberListOfEventsWithTransitions( self ):
	
		self.shouldEqual( self.machine.events, { 'CheckOut' : { 'from' : 'Shopping', 'to' : 'CheckingOut' } } )
		
	def test_MachineShouldTransitionToCheckingOutUponTriggerCheckOutEvent( self ):
	
		self.machine.trigger( 'CheckOut' )
		self.shouldEqual( self.machine.state, 'CheckingOut' )

if __name__ == '__main__':
	suite = []
	suite += unittest.TestLoader().loadTestsFromTestCase( machine_spec )
	alltests = unittest.TestSuite( suite )
	unittest.TextTestRunner( verbosity=2 ).run( alltests )