import behaviour
import unittest

import machine

class machine_spec( behaviour.Behaviour ):

	def setUp( self ):
	
		self.machine = machine.Machine()

	def test_MachineShouldInitiallyHaveStateOfInitial( self ):
	
		self.shouldEqual( self.machine.state, 'Initial' )

if __name__ == '__main__':
	suite = []
	suite += unittest.TestLoader().loadTestsFromTestCase( machine_spec )
	alltests = unittest.TestSuite( suite )
	unittest.TextTestRunner( verbosity=2 ).run( alltests )