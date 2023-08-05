#!/usr/bin/env python
# coding=utf-8
"""


"""
__docformat__ = "restructuredtext en"

import sys
import dequeue


class EmptyPhraseError( Exception ):
	pass


class SpecNamer():
	"""
	Converts a behaviour name from lower_case_with_underscores or from CamelCase
	to a Capitalised english phrase.

	Handles acronyms and numerics embedded in the words.

	"""

	def __init__( self, name ):
		"""
		Stores the name and converts it to a phrase for retrieve when required.
		"""

		self.name = name
		self.phrase = self._nameToPhrase( self.name )


	def _nameToPhrase( self, name ):
		"""
		Convert the name to a phrase by breaking it into chunks (separated by
		underscores), processing each chunk, adding it to the result, and changing
		the first letter to uppercase.

		Parameters
		----------

		name : *string*
			The name to convert into an English phrase.

		Returns
		-------

		string
			The phrase.

		"""

		def _processChunk( dq ):
			"""
			Pops the first chunk off the dq. It it is all one case, returns it,
			otherwise it breaks it into smaller chunks, pushing them back onto
			the dq, and returning just the first small chunk.
			"""

			def _lower( char ):
				return char == char.lower()

			def _upper( char ):
				return char == char.upper()

			def _numeric( char ):
				return char in ( '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' )

			chunk = dq.pop()
			if chunk == chunk.upper() or chunk == chunk.lower():
				return chunk

			while chunk:
				hasLower = False
				token = ''
				while chunk and _numeric( chunk[-1] ):
					token = chunk[-1] + token
					chunk = chunk[:-1]
				while chunk and ( _lower( chunk[-1] ) or _numeric( chunk[-1] ) ):
					token = chunk[-1] + token
					chunk = chunk[:-1]
					hasLower = True
				if chunk and _upper( chunk[-1] ):
					if hasLower:
						token = chunk[-1].lower() + token
						chunk = chunk[:-1]
					else:
						while chunk and ( _upper( chunk[-1] ) or _numeric( chunk[-1] ) ):
							token = chunk[-1] + token
							chunk = chunk[:-1]
				dq.push( token )

			return dq.pop()

		chunks = name.split( "_" )
		dq = dequeue.DeQueue( chunks )
		chunk = chunks[0]
		phrase = _processChunk( dq )

		while not dq.isEmpty():
			phrase = phrase + ' ' + _processChunk( dq )

		phrase = self._stripPrefixAndSuffix( phrase )

		return phrase[0].upper() + phrase[1:]


	def _stripPrefixAndSuffix( self, phrase ):
		"""
		Strips the words test, spec, and specificaton from the ends of the name.

		Parameters
		----------

		phrase : *string*
			The phrase to remove the prefixes and suffixes from.

		Returns
		-------

		string
			The phrase with the prefixes and suffixes removed.

		Raises
		------

		EmptyPhrase
			The phrase with the prefixes and suffixes removed is empty.

		"""

		words = phrase.split( " " )
		if words[0] in ( "test", "spec", "specification" ):
			words = words[1:]
		if words[-1] in ( "test", "spec", "specification" ):
			words = words[:-1]
		if not words:
			raise EmptyPhraseError, """Phrase '%s' consists of prefixes and suffixes only.""" % phrase
		phrase = words[0]
		for word in words[1:]:
			phrase = phrase + ' ' + word
		return phrase