# coding=utf-8
# Bootstrap for setuotools

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
	name = "Behaviour",
	version = "0.1a2",
	packages = find_packages(),
	package_data = { '': [ '*.txt', '*.rst', '*.pdf' ] },
	
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
.. _A New Look at Test-Driven Development: http://blog.daveastels.com/files/BDD_Intro.pdf""",

	classifiers = [ "Development Status :: 3 - Alpha", "Environment :: Console", "Intended Audience :: Developers",
					"License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
					"Operating System :: OS Independent", "Operating System :: MacOS :: MacOS X",
					"Operating System :: Microsoft :: Windows", "Operating System :: Unix",
					"Programming Language :: Python", "Topic :: Software Development :: Testing" ],
	
	# Unit test suite
	
	test_suite = "behaviour.test.test_behaviour.py" )