class Machine():

	def __init__( self, states ):
	
		self.states = states
		self.state = self.states[0]

	def trigger( self, event ):
	
		self.state = self.events[ event ][ 'to' ]
