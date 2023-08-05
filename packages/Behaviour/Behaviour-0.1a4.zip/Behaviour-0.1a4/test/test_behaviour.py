#!/usr/bin/env python
# coding=utf-8
'''
Unit tests for behaviour.py
'''
__docformat__ = "restructuredtext en"

import sys
import types
import unittest
import re
import decimal

import behaviour
	
class MyString( str ):
	pass

class MyTuple( tuple ):
	pass

class MyList( list ):
	pass

class MyDict( dict ):
	pass


def _testForFailure( parent, wantException, wantMessage, executable, *args, **kwargs ):
	"""
	Utility function for running tests which are meant to reject for some reason.
	
	Parameters
	----------
	
	parent : *Behaviour*
		The behaviour object being tested, needed so that unittest.fail can be located.

	wantException : *Exception*
		The exception type that should be raised.

	wantMessage : *string*
		The exception text message that should be raised.

	executable : *function/method*
		The method within Behaviour to test.

	*args : *any*
		Any arguments to be passed to the method.

	**kwargs : *any*
		Any keyword arguments to be passed to the method.

	isRE : *boolean*
		wantMessage is a regular expression to match.
	
	Algorithm
	---------
	
	Call the executable, passing through the arguments.
	Trap any exception of the specified type (good):
		Check that the exception message is correct (good):
		If not (bad) -> error message
	Trap any other exception (bad) -> error message
	Check no exception was raised (bad) -> error message
	"""

	def _getExecutableName( executable ):
		"""
		Returns the name of the executable module.
		"""

		if hasattr( executable, '__name__' ):
			return executable.__name__
		else:
			return str( executable )
			
	# trap keyword argument isRE

	if 'isRE' in kwargs:
		isRE = kwargs[ 'isRE' ]
		del kwargs[ 'isRE' ]
	else:
		isRE = False
			
	# trap keyword argument passMessage

	if 'passMessage' in kwargs:
		passMessage = kwargs[ 'passMessage' ]
		del kwargs[ 'passMessage' ]
		if passMessage:
			kwargs[ 'exceptionMsg' ] = wantMessage
				
	try:
		executable( *args, **kwargs )
	except wantException, ex:  # Correct type of exception raised
		if not isRE and str( ex ) == wantMessage:  # Check if right message raised (using RE pattern)
			return True
		elif isRE and re.match( wantMessage, str( ex ) ) != None:  # Check if right message raised (exact match)
			return True
		else:
			parent.fail( """Behaviour.%s: Raised error class '%s' message '%s', expected message '%s'.""" % \
						 ( _getExecutableName( executable ), str( type( ex ) ), str( ex ), wantMessage ) )
	except Exception, ex:  # Wrong exception raised
		parent.fail( """Behaviour.%s: Raised error class '%s' message '%s', expected error class '%s' message '%s'.""" % \
					 ( _getExecutableName( executable ), str( type( ex ) ), str( ex ), str( wantException ), wantMessage ) )
	else:  # No exception raised
		parent.fail( """Behaviour.%s: Did not raise error class '%s' message '%s'.""" % \
					 ( _getExecutableName( executable ), str( type( wantException ) ), wantMessage ) )


class TestShouldEqual( unittest.TestCase ):
	"""
	Tests the shouldEqual function:
	
	- Tests that two equal values are accepted.
	- Tests that two equal values, but of different types ( long, float ) are accepted.
	
	- Tests that two unequal values are rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()

	def test_shouldEqual_accepts_equal( self ):
		self.behave.shouldEqual( 1, 1 )

	def test_shouldEqual_accepts_equal_compatible( self ):
		self.behave.shouldEqual( 1, 1.0 )

	def test_shouldEqual_rejects_notEqual( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldEqual: Actual value (1) should equal expected value (2).",
						 self.behave.shouldEqual, 1, 2 )


class TestShouldNotEqual( unittest.TestCase ):
	"""
	Tests the shouldEqual function:
	
	- Tests that two unequal values are accepted.
	
	- Tests that two equal values are rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()
	
	def test_shouldNotEqual_accepts_notEqual( self ):
		self.behave.shouldNotEqual( 1, 2 )

	def test_shouldNotEqual_rejects_equal( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotEqual: Actual value (1) should not equal unexpected value (1).",
						 self.behave.shouldNotEqual, 1, 1 )


class TestShouldApproximatelyEqual( unittest.TestCase ):
	"""
	Tests the shouldEqual function:
	
	- Tests that two equal values are accepted.
	- Tests that two unequal values, but within the specified tolerance, are accepted.
	
	- Tests that two unequal values, but not quite within the specified tolerance, are rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a non-numeric actual value is rejected.
	- Tests that a non-numeric expected value is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()

	def test_shouldApproximatelyEqual_accepts_equal( self ):
		self.behave.shouldApproximatelyEqual( 1, 1, significantDigits=10 )

	def test_shouldApproximatelyEqual_accepts_almostEqual( self ):
		self.behave.shouldApproximatelyEqual( 1.00000000009, 1, significantDigits=10 )

	def test_shouldApproximatelyEqual_rejects_notQuiteEqual( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldApproximatelyEqual: Actual value (1.00000000011) should approximately equal expected value (1) to 10 significant digits. Allowable difference is 1e-10, actual difference is 1.10000009101e-10.",
						 self.behave.shouldApproximatelyEqual, 1.00000000011, 1, significantDigits=10 )

	def test_shouldApproximatelyEqual_rejects_nonNumeric_actual( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldApproximatelyEqual: Type (<type 'str'>) value (spam) cannot be used, must be a number.",
						 self.behave.shouldApproximatelyEqual, 1, 'spam' )

	def test_shouldApproximatelyEqual_rejects_nonNumeric_expected( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldApproximatelyEqual: Type (<type 'tuple'>) value ((1, 2)) cannot be used, must be a number.",
						 self.behave.shouldApproximatelyEqual, ( 1, 2 ), 1 )


class TestShouldNotApproximatelyEqual( unittest.TestCase ):
	"""
	Tests the shouldEqual function:
	
	- Tests that two unequal values, but not quite within the specified tolerance, are accepted.
	
	- Tests that two unequal values, but within the specified tolerance, are rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a non-numeric actual value is rejected.
	- Tests that a non-numeric expected value is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()
	
	def test_shouldNotApproximatelyEqual_accepts_notQuiteEqual( self ):
		self.behave.shouldNotApproximatelyEqual( 1.00000000011, 1, significantDigits=10 )
	
	def test_shouldNotApproximatelyEqual_rejects_almostEqual( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotApproximatelyEqual: Actual value (1.00000000009) should not approximately equal unexpected value (1) to 10 significant digits. Allowable difference is 1e-10, actual difference is 9.00000074466e-11.",
						 self.behave.shouldNotApproximatelyEqual, 1.00000000009, 1, significantDigits=10 )

	def test_shouldNotApproximatelyEqual_rejects_nonNumeric_actual( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldNotApproximatelyEqual: Type (<type 'list'>) value ([1, 2]) cannot be used, must be a number.",
						 self.behave.shouldNotApproximatelyEqual, 1, [ 1, 2 ] )
	
	def test_shouldNotApproximatelyEqual_rejects_nonNumeric_expected( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldNotApproximatelyEqual: Type (<type 'dict'>) value ({1: 'spam'}) cannot be used, must be a number.",
						 self.behave.shouldNotApproximatelyEqual, { 1: 'spam' }, 1 )


class TestShouldBeSameAs( unittest.TestCase ):
	"""
	Tests the shouldBeSameAs function:
	
	- Tests that two references to the same object are accepted.
	
	- Tests that two different objects with equal values are rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()
		self.object = []

	def test_shouldBeSameAs_accepts_same( self ):
		self.same = self.object
		self.behave.shouldBeSameAs( self.object, self.same )
		
	def test_shouldBeSameAs_rejects_different( self ):
		self.same = self.object
		_testForFailure( self.behave,
						 AssertionError, "Behaviour\.shouldBeSameAs\: Actual object id \(.+\) value \(\[\]\) should be the expected object id \(.+\) value \(\[\]\)\.",
						 self.behave.shouldBeSameAs, self.object, [], isRE=True )


class TestShouldNotBeSameAs( unittest.TestCase ):
	"""
	Tests the shouldBeSameAs function:
	
	- Tests that two different objects with equal values are rejected.
	
	- Tests that two references to the same object are rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()
		self.object = []
	
	def test_shouldNotBeSameAs_accepts_different( self ):
		self.behave.shouldNotBeSameAs( self.object, [] )
		
	def test_shouldNotBeSameAs_rejects_same( self ):
		self.same = self.object
		_testForFailure( self.behave,
						 AssertionError, "Behaviour\.shouldNotBeSameAs: Actual object id \(.+\) value \(\[\]\) should not be the unexpected object id \(.+\) value \(\[\]\).",
						 self.behave.shouldNotBeSameAs, self.object, self.same, isRE=True )


class TestShouldMatch( unittest.TestCase ):
	"""
	Tests the shouldMatch function:
	
	- Tests that a string matching the regular expression is accepted.
	- Tests that a subclass of string matching the regular expression is accepted.
	
	- Tests that a string not matching the regular expression is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a non-string string is rejected.
	- Tests that a non-string regular expression is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()

	def test_shouldMatch_accepts_match( self ):
		self.behave.shouldMatch( 'spam and eggs', '.+and.+' )

	def test_shouldMatch_accepts_match_subclassOfString( self ):
		self.behave.shouldMatch( 'spam and eggs', '.+and.+' )
		
	def test_shouldMatch_rejects_mismatch( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldMatch: Actual value (spam and eggs) should match the regular expression pattern (.+but.+).",
						 self.behave.shouldMatch, 'spam and eggs', '.+but.+' )
		
	def test_shouldMatch_rejects_nonStringActual( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldMatch: Type (<type 'int'>) value (12345) cannot be used, must be a string.",
						 self.behave.shouldMatch, 12345, '.+but.+' )
		
	def test_shouldMatch_rejects_nonStringPattern( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldMatch: Type (<type 'int'>) value (12345) cannot be used, must be a string.",
						 self.behave.shouldMatch, 'spam and eggs', 12345 )


class TestShouldNotMatch( unittest.TestCase ):
	"""
	Tests the shouldNotMatch function:
	
	- Tests that a string not matching the regular expression is accepted.
	
	- Tests that a string matching the regular expression is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a non-string string is rejected.
	- Tests that a non-string regular expression is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()
	
	def test_shouldNotMatch_accepts_mismatch( self ):
		self.behave.shouldNotMatch( 'spam and eggs', '.+but.+' )
		
	def test_shouldNotMatch_rejects_match( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotMatch: Actual value (spam and eggs) should not match the regular expression pattern (.+and.+).",
						 self.behave.shouldNotMatch, 'spam and eggs', '.+and.+' )
		
	def test_shouldNotMatch_rejects_nonStringActual( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldNotMatch: Type (<type 'int'>) value (12345) cannot be used, must be a string.",
						 self.behave.shouldNotMatch, 12345, '.+but.+' )
		
	def test_shouldNotMatch_rejects_nonStringPattern( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldNotMatch: Type (<type 'int'>) value (12345) cannot be used, must be a string.",
						 self.behave.shouldNotMatch, 'spam and eggs', 12345 )


class TestShouldBeNone( unittest.TestCase ):
	"""
	Tests the shouldBeNone function:
	
	- Tests that None is accepted.
	
	- Tests that a value other than None is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()

	def test_shouldBeNone_accepts_None( self ):
		self.behave.shouldBeNone( None )
		
	def test_shouldBeNone_rejects_notNone( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldBeNone: Actual value (0) should be None.",
						 self.behave.shouldBeNone, 0 )


class TestShouldNotBeNone( unittest.TestCase ):
	"""
	Tests the shouldNotBeNone function:
	
	- Tests that a value other than None is accepted.
	
	- Tests that None is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()
	
	def test_shouldNotBeNone_accepts_zero( self ):
		self.behave.shouldNotBeNone( 0 )
	
	def test_shouldNotBeNone_accepts_blank( self ):
		self.behave.shouldNotBeNone( '' )
		
	def test_shouldNotBeNone_rejects_None( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotBeNone: Actual value (None) should not be None.",
						 self.behave.shouldNotBeNone, None )


class TestShouldBeZero( unittest.TestCase ):
	"""
	Tests the shouldBeZero function:
	
	- Tests that integer 0 is accepted.
	- Tests that floating point 0 is accepted.
	- Tests that decimal 0 is accepted.
	
	- Tests that non-zero is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a non-numeric value is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()

	def test_shouldBeZero_accepts_zero_integer( self ):
		self.behave.shouldBeZero( 0 )

	def test_shouldBeZero_accepts_zero_float( self ):
		self.behave.shouldBeZero( 0.0 )

	def test_shouldBeZero_accepts_zero_decimal( self ):
		self.behave.shouldBeZero( decimal.Decimal( '0.0' ) )
		
	def test_shouldBeZero_rejects_nonZero( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldBeZero: Actual value (1) should be Zero.",
						 self.behave.shouldBeZero, 1 )
		
	def test_shouldBeZero_rejects_notNumber( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldBeZero: Type (<type 'str'>) value (spam) cannot be used, must be a number.",
						 self.behave.shouldBeZero, 'spam' )


class TestShouldNotBeZero( unittest.TestCase ):
	"""
	Tests the shouldNotBeZero function:
	
	- Tests that a value other than 0 is accepted.
	
	- Tests that integer 0 is rejected.
	- Tests that floating point 0 is rejected.
	- Tests that decimal 0 is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a non-numeric value is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()
	
	def test_shouldNotBeZero_accepts_nonZero( self ):
		self.behave.shouldNotBeZero( 1 )
		
	def test_shouldNotBeZero_rejects_zero_integer( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotBeZero: Actual value (0) should not be Zero.",
						 self.behave.shouldNotBeZero, 0 )
		
	def test_shouldNotBeZero_rejects_zero_float( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotBeZero: Actual value (0.0) should not be Zero.",
						 self.behave.shouldNotBeZero, 0.0 )
		
	def test_shouldNotBeZero_rejects_zero_decimal( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotBeZero: Actual value (0) should not be Zero.",
						 self.behave.shouldNotBeZero, decimal.Decimal( 0 ) )
		
	def test_shouldNotBeZero_rejects_notNumber( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldNotBeZero: Type (<type 'str'>) value (spam) cannot be used, must be a number.",
						 self.behave.shouldNotBeZero, 'spam' )


class TestShouldBeTrue( unittest.TestCase ):
	"""
	Tests the shouldBeTrue function:
	
	- Tests that True is accepted.
	
	- Tests that False is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a non-boolean value is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()

	def test_shouldBeTrue_accepts_True( self ):
		self.behave.shouldBeTrue( True )
		
	def test_shouldBeTrue_rejects_False( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldBeTrue: Actual value (False) should be True.",
						 self.behave.shouldBeTrue, False )
		
	def test_shouldBeTrue_rejects_notBoolean( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldBeTrue: Type (<type 'str'>) value (spam) cannot be used, must be a boolean (True or False).",
						 self.behave.shouldBeTrue, 'spam' )


class TestShouldBeFalse( unittest.TestCase ):
	"""
	Tests the shouldBeFalse function:
	
	- Tests that False is accepted.
	
	- Tests that True is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a non-boolean value is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()
	
	def test_shouldBeFalse_accepts_False( self ):
		self.behave.shouldBeFalse( False )
		
	def test_shouldBeFalse_rejects_True( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldBeFalse: Actual value (True) should be False.",
						 self.behave.shouldBeFalse, True )
		
	def test_shouldBeTrue_rejects_notBoolean( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldBeFalse: Type (<type 'int'>) value (12345) cannot be used, must be a boolean (True or False).",
						 self.behave.shouldBeFalse, 12345 )


class TestShouldBeEmpty( unittest.TestCase ):
	"""
	Tests the shouldBeEmpty function:
	
	- Tests that the empty string '' is accepted.
	- Tests that an empty subclass of string is accepted.
	- Tests that the empty tuple () is accepted.
	- Tests that an empty subclass of tuple is accepted.
	- Tests that the empty list [] is accepted.
	- Tests that an empty subclass of list is accepted.
	- Tests that the empty dictionary {} is accepted.
	- Tests that an empty subclass of dictionary is accepted.
	
	- Tests that a non-empty string is rejected.
	- Tests that a non-empty tuple is rejected.
	- Tests that a non-empty list is rejected.
	- Tests that a non-empty dictionary is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a dictionary check with a non-tuple item is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()

	def test_shouldBeEmpty_accepts_empty_string( self ):
		self.behave.shouldBeEmpty( '' )

	def test_shouldBeEmpty_accepts_empty_string_subclass( self ):
		self.behave.shouldBeEmpty( MyString( '' ) )

	def test_shouldBeEmpty_accepts_empty_tuple( self ):
		self.behave.shouldBeEmpty( () )

	def test_shouldBeEmpty_accepts_empty_tuple_subclass( self ):
		self.behave.shouldBeEmpty( MyTuple( () ) )

	def test_shouldBeEmpty_accepts_empty_list( self ):
		self.behave.shouldBeEmpty( [] )

	def test_shouldBeEmpty_accepts_empty_list_subclass( self ):
		self.behave.shouldBeEmpty( MyList( [] ) )

	def test_shouldBeEmpty_accepts_empty_dict( self ):
		self.behave.shouldBeEmpty( {} )

	def test_shouldBeEmpty_accepts_empty_dict_subclass( self ):
		self.behave.shouldBeEmpty( MyDict( {} ) )
		
	def test_shouldBeEmpty_rejects_nonEmpty_string( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldBeEmpty: Actual value (spam) should be empty.",
						 self.behave.shouldBeEmpty, 'spam' )
		
	def test_shouldBeEmpty_rejects_nonEmpty_tuple( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldBeEmpty: Actual value (spam) should be empty.",
						 self.behave.shouldBeEmpty, ( 'spam' ) )
		
	def test_shouldBeEmpty_rejects_nonEmpty_list( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldBeEmpty: Actual value (['spam']) should be empty.",
						 self.behave.shouldBeEmpty, [ 'spam' ] )
		
	def test_shouldBeEmpty_rejects_nonEmpty_dict( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldBeEmpty: Actual value ({1: 'spam'}) should be empty.",
						 self.behave.shouldBeEmpty, { 1: 'spam' } )
		
	def test_shouldBeEmpty_rejects_notSequenceOrMapping( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldBeEmpty: Type (<type 'int'>) value (12345) cannot be used, must be a sequence or mapping.",
						 self.behave.shouldBeEmpty, 12345 )


class TestShouldNotBeEmpty( unittest.TestCase ):
	"""
	Tests the shouldNotBeEmpty function:
	
	- Tests that a non-empty string is accepted.
	- Tests that a non-empty subclass of string is accepted.
	- Tests that a non-empty tuple is accepted.
	- Tests that a non-empty subclass of tuple is accepted.
	- Tests that a non-empty list is accepted.
	- Tests that a non-empty subclass of list is accepted.
	- Tests that a non-empty dictionary is accepted.
	- Tests that a non-empty subclass of dictionary is accepted.
	
	- Tests that the empty string '' is rejected.
	- Tests that the empty tuple () is rejected.
	- Tests that the empty list [] is rejected.
	- Tests that the empty dictionary {} is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a non-sequence and non-mapping type is rejected. This test ensures:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()
	
	def test_shouldNotBeEmpty_accepts_nonEmpty_string( self ):
		self.behave.shouldNotBeEmpty( 'spam' )
	
	def test_shouldNotBeEmpty_accepts_nonEmpty_string_subclass( self ):
		self.behave.shouldNotBeEmpty( MyString( 'spam' ) )
	
	def test_shouldNotBeEmpty_accepts_nonEmpty_tuple( self ):
		self.behave.shouldNotBeEmpty( ( 'spam' ) )
	
	def test_shouldNotBeEmpty_accepts_nonEmpty_tuple_subclass( self ):
		self.behave.shouldNotBeEmpty( MyTuple( ( 'spam' ) ) )
	
	def test_shouldNotBeEmpty_accepts_nonEmpty_list( self ):
		self.behave.shouldNotBeEmpty( [ 'spam' ] )
	
	def test_shouldNotBeEmpty_accepts_nonEmpty_list_subclass( self ):
		self.behave.shouldNotBeEmpty( MyList( [ 'spam' ] ) )
	
	def test_shouldNotBeEmpty_accepts_nonEmpty_dict( self ):
		self.behave.shouldNotBeEmpty( { 1: 'spam' } )
	
	def test_shouldNotBeEmpty_accepts_nonEmpty_dict_subclass( self ):
		self.behave.shouldNotBeEmpty( MyDict( { 1: 'spam' } ) )
		
	def test_shouldNotBeEmpty_rejects_empty_string( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotBeEmpty: Actual value () should be not empty.",
						 self.behave.shouldNotBeEmpty, '' )
		
	def test_shouldNotBeEmpty_rejects_empty_tuple( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotBeEmpty: Actual value (()) should be not empty.",
						 self.behave.shouldNotBeEmpty, () )
		
	def test_shouldNotBeEmpty_rejects_empty_list( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotBeEmpty: Actual value ([]) should be not empty.",
						 self.behave.shouldNotBeEmpty, [] )
		
	def test_shouldNotBeEmpty_rejects_empty_dict( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotBeEmpty: Actual value ({}) should be not empty.",
						 self.behave.shouldNotBeEmpty, {} )
		
	def test_shouldNotBeEmpty_rejects_notSequenceOrMapping( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldNotBeEmpty: Type (<type 'int'>) value (12345) cannot be used, must be a sequence or mapping.",
						 self.behave.shouldNotBeEmpty, 12345 )


class TestShouldInclude( unittest.TestCase ):
	"""
	Tests the shouldInclude function:
	
	- Tests that the a string containing the substring is accepted.
	- Tests that a subclass of string containing the substring is accepted.
	- Tests that a tuple containing the item is accepted.
	- Tests that a subclass of tuple containing the item is accepted.
	- Tests that a list containing the item is accepted.
	- Tests that a subclass of list containing the item is accepted.
	- Tests that a dictionary containing the item is accepted.
	- Tests that a subclass of dictionary containing the item is accepted.
	
	- Tests that a string not containing the substring is rejected.
	- Tests that a tuple not containing the item is rejected.
	- Tests that a list not containing the item is rejected.
	- Tests that a dictionary not containing the key is rejected.
	- Tests that a dictionary containing the key, but with different data, is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a dictionary check with a non-tuple item is rejected.
	- Tests that a dictionary check with a tuple item of the wrong cardinality is rejected.
	- Tests that a non-sequence and non-mapping type is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()

	def test_shouldInclude_accepts_member_string( self ):
		self.behave.shouldInclude( 'spam, eggs, sausage', 'eggs' )

	def test_shouldInclude_accepts_member_string_subclass( self ):
		self.behave.shouldInclude( MyString( 'spam, eggs, sausage' ), 'eggs' )

	def test_shouldInclude_accepts_member_tuple( self ):
		self.behave.shouldInclude( ( 'spam', 'eggs', 'sausage' ), 'eggs' )

	def test_shouldInclude_accepts_member_tuple_subclass( self ):
		self.behave.shouldInclude( MyTuple( ( 'spam', 'eggs', 'sausage' ) ), 'eggs' )

	def test_shouldInclude_accepts_member_list( self ):
		self.behave.shouldInclude( [ 'spam', 'eggs', 'sausage' ], 'eggs' )

	def test_shouldInclude_accepts_member_list_subclass( self ):
		self.behave.shouldInclude( MyList( [ 'spam', 'eggs', 'sausage' ] ), 'eggs' )

	def test_shouldInclude_accepts_member_dict( self ):
		self.behave.shouldInclude( { 1: 'spam', 2: 'eggs', 3: 'sausage' }, ( 2, 'eggs' ) )

	def test_shouldInclude_accepts_member_dict_subclass( self ):
		self.behave.shouldInclude( MyDict( { 1: 'spam', 2: 'eggs', 3: 'sausage' } ), ( 2, 'eggs' ) )
		
	def test_shouldInclude_rejects_nonMember_string( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldInclude: String (spam, eggs, sausage) should include item (bacon).",
						 self.behave.shouldInclude, 'spam, eggs, sausage', 'bacon' )
		
	def test_shouldInclude_rejects_nonMember_tuple( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldInclude: Tuple (('spam', 'eggs', 'sausage')) should include item (bacon).",
						 self.behave.shouldInclude, ( 'spam', 'eggs', 'sausage' ), 'bacon' )
		
	def test_shouldInclude_rejects_nonMember_list( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldInclude: List (['spam', 'eggs', 'sausage']) should include item (bacon).",
						 self.behave.shouldInclude, [ 'spam', 'eggs', 'sausage' ], 'bacon' )
		
	def test_shouldInclude_rejects_nonMember_dict_missingKey( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldInclude: Dictionary ({1: 'spam', 2: 'eggs', 3: 'sausage'}) should include key (4).",
						 self.behave.shouldInclude, { 1: 'spam', 2: 'eggs', 3: 'sausage' }, ( 4, 'eggs' ) )
		
	def test_shouldInclude_rejects_nonMember_dict_hasKeyButDifferentData( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldInclude: Dictionary ({1: 'spam', 2: 'eggs', 3: 'sausage'}) should include key (2) data (bacon).",
						 self.behave.shouldInclude, { 1: 'spam', 2: 'eggs', 3: 'sausage' }, ( 2, 'bacon' ) )
		
	def test_shouldInclude_rejects_notSequenceorMapping( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldInclude: Type (<type 'int'>) value (12345) cannot be used, must be a sequence or mapping.",
						 self.behave.shouldInclude, 12345, 234 )
		
	def test_shouldInclude_rejects_dict_itemNot2Tuple( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldInclude: Item ((2, 'eggs', 'junk')) must be a 2-tuple ( key, data ).",
						 self.behave.shouldInclude, { 1: 'spam', 2: 'eggs', 3: 'sausage' }, ( 2, 'eggs', 'junk' ) )
		
	def test_shouldInclude_rejects_dict_itemNotATuple( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldInclude: Item (2) type (<type 'int'>) must be a 2-tuple ( key, data ).",
						 self.behave.shouldInclude, { 1: 'spam', 2: 'eggs', 3: 'sausage' }, 2 )


class TestShouldNotInclude( unittest.TestCase ):
	"""
	Tests the shouldNotInclude function:
	
	- Tests that a string not containing the substring is accepted.
	- Tests that a tuple not containing the item is accepted.
	- Tests that a list not containing the item is accepted.
	- Tests that a dictionary not containing the key is accepted.
	- Tests that a dictionary containing the key, but with different data, is accepted.
	
	- Tests that the a string containing the substring is rejected.
	- Tests that a tuple containing the item is rejected.
	- Tests that a list containing the item is rejected.
	- Tests that a dictionary containing the item is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a dictionary check with a non-tuple item is rejected.
	- Tests that a dictionary check with a tuple item of the wrong cardinality is rejected.
	- Tests that a non-sequence and non-mapping type is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()

	def test_shouldNotInclude_accepts_nonMember_string( self ):
		self.behave.shouldNotInclude( 'spam, eggs, sausage', 'bacon' )

	def test_shouldNotInclude_accepts_nonMember_tuple( self ):
		self.behave.shouldNotInclude( ( 'spam', 'eggs', 'sausage' ), 'bacon' )

	def test_shouldNotInclude_accepts_nonMember_list( self ):
		self.behave.shouldNotInclude( [ 'spam', 'eggs', 'sausage' ], 'bacon' )

	def test_shouldNotInclude_accepts_nonMember_dict_missingKey( self ):
		self.behave.shouldNotInclude( { 1: 'spam', 2: 'eggs', 3: 'sausage' }, ( 4, 'eggs' ) )

	def test_shouldNotInclude_accepts_nonMember_dict_hasKey_differentData( self ):
		self.behave.shouldNotInclude( { 1: 'spam', 2: 'eggs', 3: 'sausage' }, ( 2, 'bacon' ) )
		
	def test_shouldNotInclude_rejects_member_string( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotInclude: String (spam, eggs, sausage) should not include item (eggs).",
						 self.behave.shouldNotInclude, 'spam, eggs, sausage', 'eggs' )
		
	def test_shouldNotInclude_rejects_member_tuple( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotInclude: Tuple (('spam', 'eggs', 'sausage')) should not include item (eggs).",
						 self.behave.shouldNotInclude, ( 'spam', 'eggs', 'sausage' ), 'eggs' )
		
	def test_shouldNotInclude_rejects_member_list( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldNotInclude: List (['spam', 'eggs', 'sausage']) should not include item (eggs).",
						 self.behave.shouldNotInclude, [ 'spam', 'eggs', 'sausage' ], 'eggs' )
		
	def test_shouldNotInclude_rejects_member_dict( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldInclude: Dictionary ({1: 'spam', 2: 'eggs', 3: 'sausage'}) should not include key (2) data (eggs).",
						 self.behave.shouldNotInclude, { 1: 'spam', 2: 'eggs', 3: 'sausage' }, ( 2, 'eggs' ) )
		
	def test_shouldNotInclude_rejects_notSequenceorMapping( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldNotInclude: Type (<type 'float'>) value (12345.6789) cannot be used, must be a sequence or mapping.",
						 self.behave.shouldNotInclude, 12345.6789, 234 )
		
	def test_shouldNotInclude_rejects_dict_itemNot2Tuple( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldNotInclude: Item ((2, 'eggs', 'junk')) must be a 2-tuple ( key, data ).",
						 self.behave.shouldNotInclude, { 1: 'spam', 2: 'eggs', 3: 'sausage' }, ( 2, 'eggs', 'junk' ) )
		
	def test_shouldNotInclude_rejects_dict_itemNotATuple( self ):
		_testForFailure( self.behave,
						 TypeError, "Behaviour.shouldNotInclude: Item (2) type (<type 'int'>) must be a 2-tuple ( key, data ).",
						 self.behave.shouldNotInclude, { 1: 'spam', 2: 'eggs', 3: 'sausage' }, 2 )


class TestShouldRaiseException( unittest.TestCase ):
	"""
	Tests the shouldRaiseException function:
	
	- Tests that raising the correct exception type accepted.
	
	- Tests that not raising any exception is rejected.
	- Tests that raising the wrong exception type is rejected.
	- Tests that raising the right exception type, but with the wrong message pattern, is rejected.
	- Tests that raising the right exception type, but with the wrong arguments pattern, is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is an AssertionError
	  - the AssertionError returns to right error message.
	  
	- Tests that a dictionary check with a non-tuple item is rejected.
	- Tests that a dictionary check with a tuple item of the wrong cardinality is rejected.
	- Tests that a non-sequence and non-mapping type is rejected. These tests ensure:
	  - an exception was raised
	  - the raised exception is a TypeError
	  - the TypeError returns to right error message.
	"""

	def _divideByZero( self, first, second=0 ):
		return first / second

	def setUp( self ):
		self.behave = behaviour.Behaviour()
		
	def test_shouldRaiseException_accepts_exception( self ):
		self.behave.shouldRaiseException( ZeroDivisionError, self._divideByZero, 1 )
		
	def test_shouldRaiseException_accepts_exception_rightArgs( self ):
		self.behave.shouldRaiseException( ZeroDivisionError, self._divideByZero, 1, exceptionArgs=('integer division or modulo by zero',) )
		
	def test_shouldRaiseException_accepts_exception_rightPattern( self ):
		self.behave.shouldRaiseException( ZeroDivisionError, self._divideByZero, 1, exceptionPattern=".*integer division.+by zero.*" )
	
	def test_ShouldRaiseException_rejects_noException( self ):
		try:
			self.behave.shouldRaiseException( ZeroDivisionError, self._divideByZero, 1, second=2 )
		except AssertionError, ex:
			wantMsg = "Behaviour.shouldRaiseException: Executable (_divideByZero) should raise exception (%s), got exception (%s)."
			if str( ex ) == wantMsg:
				pass
			else:
				self.fail( '''Behaviour.shouldRaiseException: Executable (_divideByZero) raised error message (%s), expected message (%s)''' % \
						   ( str( ex ), wantMsg ) )
		except Exception, ex:
			self.fail( '''Behaviour.shouldRaiseException: Executable (_divideByZero) raised error class (%s), expected an AssertionError''' % \
						   ( str( ex ) ) )
		else:
			self.fail( '''Behaviour.shouldRaiseException: Executable (_divideByZero) did not raise AssertionError.''' )

	def test_ShouldRaiseException_rejects_noException( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldApproximatelyEqual: Actual value (1.00000000011) should approximately equal expected value (1) to 10 significant digits. Allowable difference is 1e-10, actual difference is 1.10000009101e-10.",
						 self.behave.shouldApproximatelyEqual, 1.00000000011, 1, significantDigits=10 )
	
	def test_ShouldRaiseException_rejects_wrongException( self ):
		_testForFailure( self.behave,
						 AssertionError, "Behaviour.shouldRaiseException: Executable (_divideByZero) should raise exception (<type 'exceptions.ZeroDivisionError'>), got exception (<type 'exceptions.TypeError'>).",
						 self.behave.shouldRaiseException, ZeroDivisionError, self._divideByZero, 1, second='spam' )
	
	def test_ShouldRaiseException_rejects_wrongPattern( self ):
		_testForFailure( self.behave,
						 AssertionError,
						 "Behaviour.shouldRaiseException: Executable (_divideByZero) raised exception (<type 'exceptions.ZeroDivisionError'>), pattern (integer division or modulo by zero) should be pattern (Won't match!).",
						 self.behave.shouldRaiseException, ZeroDivisionError, self._divideByZero, 1, second=0, exceptionPattern="Won't match!" )
	
	def test_ShouldRaiseException_rejects_wrongArgs( self ):
		_testForFailure( self.behave,
						 AssertionError,
						 "Behaviour.shouldRaiseException: Executable (_divideByZero) raised exception (<type 'exceptions.ZeroDivisionError'>), args (('integer division or modulo by zero',)) should be args (123450).",
						 self.behave.shouldRaiseException, ZeroDivisionError, self._divideByZero, 1, second=0, exceptionArgs=123450 )


class TestReturnsGivenMessage( unittest.TestCase ):
	"""
	Tests the functions return the specified message on a failure.
	"""

	def setUp( self ):
		self.behave = behaviour.Behaviour()
	
	def test_shouldEqual_rejects_notEqual_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should equal expected.",
						 self.behave.shouldEqual, 1, 2,
						 passMessage=True )

	def test_shouldNotEqual_rejects_equal_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should not equal unexpected.",
						 self.behave.shouldNotEqual, 1, 1,
						 passMessage=True )

	def test_shouldApproximatelyEqual_rejects_notQuiteEqual_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should approximtely equal expected.",
						 self.behave.shouldApproximatelyEqual, 1.00000000011, 1, significantDigits=10,
						 passMessage=True )

	def test_shouldNotApproximatelyEqual_rejects_almostEqual_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should not approximtely equal unexpected.",
						 self.behave.shouldNotApproximatelyEqual, 1.00000000009, 1, significantDigits=10,
						 passMessage=True )

	def test_shouldBeSameAs_rejects_different_returnsGivenMessage( self ):
		self.object = []
		_testForFailure( self.behave,
						 AssertionError, "Actual should be expected.",
						 self.behave.shouldBeSameAs, self.object, [],
						 passMessage=True )

	def test_shouldNotBeSameAs_rejects_same_returnsGivenMessage( self ):
		self.object = []
		self.same = self.object
		_testForFailure( self.behave,
						 AssertionError, "Actual should not be unexpected.",
						 self.behave.shouldNotBeSameAs, self.object, self.same,
						 passMessage=True )

	def test_shouldMatch_rejects_mismatch_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should match pattern.",
						 self.behave.shouldMatch, 'spam and eggs', '.+but.+',
						 passMessage=True )
		
	def test_shouldNotMatch_rejects_match_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should not match pattern.",
						 self.behave.shouldNotMatch, 'spam and eggs', '.+and.+',
						 passMessage=True )
		
	def test_shouldBeNone_rejects_notNone_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should be None.",
						 self.behave.shouldBeNone, 0,
						 passMessage=True )

	def test_shouldNotBeNone_rejects_None_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should not be None.",
						 self.behave.shouldNotBeNone, None,
						 passMessage=True )

	def test_shouldBeZero_rejects_nonZero_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should be Zero.",
						 self.behave.shouldBeZero, 1,
						 passMessage=True )
		
	def test_shouldNotBeZero_rejects_zero_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should not be Zero.",
						 self.behave.shouldNotBeZero, 0,
						 passMessage=True )
		
	def test_shouldBeTrue_rejects_False_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should be True.",
						 self.behave.shouldBeTrue, False,
						 passMessage=True )
		
	def test_shouldBeFalse_rejects_True_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should be False.",
						 self.behave.shouldBeFalse, True,
						 passMessage=True )
		
	def test_shouldBeEmpty_rejects_nonEmpty_list_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should be empty.",
						 self.behave.shouldBeEmpty, [ 'spam' ],
						 passMessage=True )
		
	def test_shouldBeEmpty_rejects_nonEmpty_dict_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should be empty.",
						 self.behave.shouldBeEmpty, { 1: 'spam' },
						 passMessage=True )
		
	def test_shouldNotBeEmpty_rejects_empty_tuple_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should be not empty.",
						 self.behave.shouldNotBeEmpty, (),
						 passMessage=True )
		
	def test_shouldNotBeEmpty_rejects_empty_dict_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should be not empty.",
						 self.behave.shouldNotBeEmpty, {},
						 passMessage=True )
		
	def test_shouldInclude_rejects_nonMember_string_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should include item.",
						 self.behave.shouldInclude, 'spam, eggs, sausage', 'bacon',
						 passMessage=True )
		
	def test_shouldInclude_rejects_nonMember_dict_hasKeyButDifferentData_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should include item.",
						 self.behave.shouldInclude, { 1: 'spam', 2: 'eggs', 3: 'sausage' }, ( 2, 'bacon' ),
						 passMessage=True )
		
	def test_shouldNotInclude_rejects_member_list_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should not include item.",
						 self.behave.shouldNotInclude, [ 'spam', 'eggs', 'sausage' ], 'eggs',
						 passMessage=True )

	def test_shouldNotInclude_rejects_member_dict_returnsGivenMessage( self ):
		_testForFailure( self.behave,
						 AssertionError, "Actual should not include item.",
						 self.behave.shouldNotInclude, { 1: 'spam', 2: 'eggs', 3: 'sausage' }, ( 2, 'eggs' ),
						 passMessage=True )


if __name__ == '__main__':
	suite = []
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldEqual )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldNotEqual )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldApproximatelyEqual )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldNotApproximatelyEqual )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldBeSameAs )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldNotBeSameAs )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldMatch )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldNotMatch )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldBeNone )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldNotBeNone )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldBeZero )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldNotBeZero )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldBeTrue )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldBeFalse )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldBeEmpty )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldNotBeEmpty )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldInclude )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldNotInclude )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestShouldRaiseException )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestReturnsGivenMessage )
	alltests = unittest.TestSuite( suite )
	unittest.TextTestRunner( verbosity=2 ).run( alltests )
