#!/usr/bin/env python
# coding=utf-8
'''
Unit tests for specnamer.py
'''
__docformat__ = "restructuredtext en"

import sys
import unittest

import specnamer
	

class TestStripPrefixAndSuffix( unittest.TestCase ):
	"""
	Tests the SpecNamer class
	"""

	def test_ShouldStripLeadingUnderscoredTest( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "test_trial" ).phrase, "Trial" )

	def test_ShouldStripLeadingCamelCaseTest( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "TestTrial" ).phrase, "Trial" )

	def test_ShouldStripTrailingUnderscoredTest( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "trial_test" ).phrase, "Trial" )

	def test_ShouldStripTrailingCamelCaseTest( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "TrialTest" ).phrase, "Trial" )

	def test_ShouldStripLeadingUnderscoredSpec( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "spec_trial" ).phrase, "Trial" )

	def test_ShouldStripLeadingCamelCaseSpec( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "SpecTrial" ).phrase, "Trial" )

	def test_ShouldStripTrailingUnderscoredSpec( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "trial_spec" ).phrase, "Trial" )

	def test_ShouldStripTrailingCamelCaseSpec( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "TrialSpec" ).phrase, "Trial" )

	def test_ShouldStripLeadingUnderscoredSpecification( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "specification_trial" ).phrase, "Trial" )

	def test_ShouldStripLeadingCamelCaseSpecification( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "SpecificationTrial" ).phrase, "Trial" )

	def test_ShouldStripTrailingUnderscoredSpecification( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "trial_specification" ).phrase, "Trial" )

	def test_ShouldStripTrailingCamelCaseSpecification( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "TrialSpecification" ).phrase, "Trial" )

	def test_ShouldStripBothEndsWhenAffixes( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "test_trial_spec" ).phrase, "Trial" )

	def test_ShouldRaiseEmptyPhraseErrorWhenStrippedToEmpty( self ):
		self.failUnlessRaises( specnamer.EmptyPhraseError, specnamer.SpecNamer, "test_spec" )
	

class TestNametoPhrase( unittest.TestCase ):
	"""
	Tests the SpecNamer class
	"""

	def test_ShouldReturnCapitalCaseFromCapitalCase( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "Word" ).phrase, "Word" )

	def test_ShouldReturnCapitalCaseFromLowerCase( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "word" ).phrase, "Word" )

	def test_ShouldReturnUpperCaseFromUpperCase( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "ASCII" ).phrase, "ASCII" )

	def test_ShouldReturnCapitalCasePlusLowerCaseFromCapitalCasePlusCapitalCase( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "TwoWords" ).phrase, "Two words" )

	def test_ShouldReturnCapitalCasePlusLowerCaseFromLowerCasePlusLowerCase( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "two_words" ).phrase, "Two words" )

	def test_ShouldReturnCapitalCasePlusUpperCaseFromCapitalCasePlusUpperCase( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "OnlyASCII" ).phrase, "Only ASCII" )

	def test_ShouldReturnUpperCasePlusUpperCaseFromLowerCasePlusUpperCase( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "only_ASCII" ).phrase, "Only ASCII" )

	def test_ShouldReturnUpperCasePlusLowerCaseFromUpperCasePlusCapitalCase( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "ASCIIOnly" ).phrase, "ASCII only" )

	def test_ShouldReturnUpperCasePlusLowerCaseFromUpperCasePlusLowerCase( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "ASCII_only" ).phrase, "ASCII only" )

	def test_ShouldReturnTwoUpperCasesFromTwoUpperCases( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "ASCII_ANSI" ).phrase, "ASCII ANSI" )

	def test_ShouldReturnUpperCaseWithEmbeddedNosFromUpperCaseWithEmbeddedNos( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "H2O" ).phrase, "H2O" )

	def test_ShouldReturnCapitalCasePlusUpperCaseTrailingNosFromCapitalCasePlusUpperCaseTrailingNos( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "FormUB40" ).phrase, "Form UB40" )

	def test_ShouldReturnUpperCaseTrailingNosPlusLowerCaseFromUpperCaseTrailingNosPlusCapitalCase( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "HAL9000Computer" ).phrase, "HAL9000 computer" )

	def test_ShouldReturnCapitalCasePlusUpperCaseLeadingNosFromCapitalCasePlusUpperCaseLeadingNos( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "Learn123ABC" ).phrase, "Learn 123ABC" )

	def test_ShouldReturnManyWordsFromManyWords( self ):
		self.failUnlessEqual( specnamer.SpecNamer( "one_two_ThreeFOURFive_six7eight_nine" ).phrase, "One two three FOUR five six7eight nine" )


if __name__ == '__main__':
	suite = []
	suite += unittest.TestLoader().loadTestsFromTestCase( TestStripPrefixAndSuffix )
	suite += unittest.TestLoader().loadTestsFromTestCase( TestNametoPhrase )
	alltests = unittest.TestSuite( suite )
	unittest.TextTestRunner( verbosity=2 ).run( alltests )
