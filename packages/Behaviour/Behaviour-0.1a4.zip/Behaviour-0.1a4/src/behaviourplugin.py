#!/usr/bin/env python
# coding=utf-8
"""


"""
__docformat__ = "restructuredtext en"

import logging
import os
import re
import sys
import textwrap

from nose.plugins.base import Plugin

log = logging.getLogger( "nose.plugins.behaviourplugin" )


class Specification( Plugin ):
	"""
	

	"""

	def __init__( self ):
		"""
		
		"""
		
		Plugin.__init__( self )
	
	
	def options( self, parser, env=os.environ ):
		"""
		Add command-line options for this plugin.
		"""
		
		Plugin.options( parser, env=os.environ )
		
		
	def help( self ):
		"""
		Return a string for nose to use when invoked with -h.
		"""
		
		return textwrap.dedent( "Enable selection of specifications and behaviours. Also enable of converting names to English phrases for output" )
		
		
	def configure( self, options, config ):
		"""
		Configure plugin from command line options.
		"""
		
		Plugin.configure( options, config )
		
		
	def wantClass( self, cls ):
		"""
		Accept the class if its name ends with "_spec" or "Specification".
		"""
		
		if cls.__name__.endswith( "_spec" ) or cls.__name__.endswith( "Specification" ):
			return True
		else:
			return None
	
	
	def wantFunction( self, function ):
		"""
		Accept the function if its name starts with "should" or "Should".
		"""
		
		if function.__name__ == "runTest":
			return False
		if function.__name__.startswith( "should" ) or \
		   function.__name__.startswith( "Should" ):
			return True
		else:
			return None
	
	
	def wantMethod( self, method ):
		"""
		Accept the method if its name starts with "should" or "Should".
		"""
		
		if function.__name__ == "runTest":
			return False
		if method.__name__.startswith( "should" ) or \
		   method.__name__.startswith( "Should" ):
			return True
		else:
			return None