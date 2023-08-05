# coding=utf-8
# Bootstrap for setuotools

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
	name = "Behaviour",
	version = "0.1a4",
	packages = find_packages(),
	package_dir = { 'behaviour': './src' },
	package_data = { '': [ '*.txt', '*.rst', '*.pdf', '*.html', '*.css', '*.js', '*.png' ] },
    include_package_data = True,
    zip_safe = False,
    install_requires = [ 'setuptools>=0.6b1' ],
    test_suite = 'behaviour.test.test_behaviour.py',

	# PyPI metadata

	author = "Mark Dancer",
	author_email = "mark.dancer@pobox.com",
	description = "Behaviour Driven Development in Python",
	keywords = "behaviour driven development design unit test testing unittest",

	long_description = """Behaviour provides a language suitable for Behaviour Driven Development (BDD), as opposed to
post-coding unit testing. It operates as a facade over Python's unit testing framework.

What is Behaviour Driven Development?
-------------------------------------

BDD is a derivative of Test Driven Development (TDD), evolving out of the observed adoption-life-cycle
for TDD:

1. A developer starts using a unit testing framework (like unittest.py).
2. The developer becomes more confident in the quality of his work.
3. They realize that writing the tests first lets them concentrate on writing the code they needs.
4. The developer notices that the tests document the code.
5. Writing tests first helps the developer to design the API for their code.
6. The developer realizes that TDD is about defining behaviour rather than testing.
7. The developer adopts mocking as a fundamental approach to support component interactions.

BDD supports the progression through that life-cycle, particularly the last three steps.

BDD supports this transition is by providing an appropriate language. Frameworks for BDD talk about
either specifications (e.g., RSpec for Ruby, NSpec for C#.NET) or behaviours (e.g., JBehave for Java,
NBehave for .NET).

For more information on BDD, see:

- `Introducing BDD`_ by Dan North;
- `A New Look at Test-Driven Development`_ by Dave Astels;

.. _Introducing BDD: http://dannorth.net/introducing-bdd
.. _A New Look at Test-Driven Development: http://blog.daveastels.com/files/BDD_Intro.pdf

What does Behaviour do for Me?
------------------------------

Behaviour allows you to say things like: ::

	class verifyUserSpecification( behaviour.Behaviour ):

		def setUp( self ):

			self.user = User( "Mark Dancer" )

		def verifyInitialUserNameIsNameInConstructor( self ):

			self.shouldBeEqual( self.user.name, "Mark Dancer" )

		def verifyInitialUserHasNoLanguages( self ):

			self.shouldBeEmpty( self.user.languages )

This has no more expressive power than what is offered by unittest: ::

	class testUser( unittest.TestCase ):

		def setUp( self ):

			self.user = User( "Mark Dancer ")

		def testName( self ):

			self.failUnlessEqual( self.user.name, "Mark Dancer" )

		def testLanguages( self ):

			self.failUnless( self.user.languages = [] )

What it does offer is an alternative set of semantics.

With the semantics of unittest, we are testing a piece of code that
we have already written.

With Behaviour, we are writing a specification for the piece of code we are
about to write. It is much clearer with BDD that the specification is
written before the code.

""",

	classifiers = [ "Development Status :: 3 - Alpha", "Environment :: Console", "Intended Audience :: Developers",
					"License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
					"Operating System :: OS Independent", "Operating System :: MacOS :: MacOS X",
					"Operating System :: Microsoft :: Windows", "Operating System :: Unix",
					"Programming Language :: Python", "Topic :: Software Development :: Testing" ] )