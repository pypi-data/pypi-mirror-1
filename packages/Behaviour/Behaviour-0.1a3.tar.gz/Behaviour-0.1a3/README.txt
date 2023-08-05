Behaviour.py
############


Introduction
============

Behaviour provides a language suitable for Behaviour Driven Development (BDD),
as opposed to post-coding unit testing. It operates as a facade over Python's
unit testing framework.

What is Behaviour Driven Development?
-------------------------------------

BDD is a derivative of Test Driven Development (TDD), evolving out of the
observed adoption-life-cycle for TDD:

1. A developer starts using a unit testing framework (like unittest.py).
2. The developer becomes more confident in the quality of his work.
3. They realize that writing the tests first lets them concentrate on writing
   the code they needs.
4. The developer notices that the tests document the code.
5. Writing tests first helps the developer to design the API for their code.
6. The developer realizes that TDD is about defining behaviour rather than
   testing.
7. The developer adopts mocking as a fundamental approach to support component
   interactions.

BDD supports the progression through that life-cycle, particularly the last
three steps.

BDD supports this transition is by providing an appropriate language.
Frameworks for BDD talk about either specifications (e.g., RSpec for Ruby,
NSpec for C#.NET) or behaviours (e.g., JBehave for Java, NBehave for .NET).
 
For more information on BDD, see:
 
- Introducing BDD by Dan North [http://dannorth.net/introducing-bdd];
- A New Look at Test-Driven Development by Dave Astels
  [http://blog.daveastels.com/files/BDD_Intro.pdf];


What does Behaviour do for Me?
------------------------------

Behaviour allows you to say things like:

	class verifyUserSpecification( behaviour.Behaviour ):
	
	    def setUp( self ):
	    
	    	self.user = User( "Mark Dancer" )
	    	
        def verifyInitialUserNameIsNameInConstructor( self ):
        
            self.shouldBeEqual( self.user.name, "Mark Dancer" )
            
        def verifyInitialUserHasNoLanguages( self ):
        
            self.shouldBeEmpty( self.user.languages )
            
This has no more expressive power than what is offered by unittest:

    class testUser( unittest.TestCase ):
    
        def setUp( self ):
        
            self.user = User( "Mark Dancer ")
            
        def testName( self ):
        
            self.failUnlessEqual( self.user.name, "Mark Dancer" )
            
        def testLanguages( self ):
        
            self.failUnless( self.user.languages = [] )

What it does offer is an alternative set of semantics. With the semantics
of unittetst, we are testing a piece of code that we have already written.
With Behaviour, we are writing a specification for the piece of code we are
about to write. It is much clearer with BDD that the specification is 
written before the code.


Package Contents
================

authors.txt    The culprits responsible.
changes.txt    Change history.
./doc          HTML API documentation.
./example      Two examples of using Behaviour. See the readme files in each.
ez_setup.py    Bootstrap for the easy_install installation system.
faq.txt        Empty until someone asks a question.
install.txt    Instructions for installing.
license.txt    Licensing terms and conditions.
LGPL.txt       The full text of the license.
readme.txt     This file.
setup.py       Install script.
./src          Source code.
./test         Unit test suite.
thanks.txt     The inspiration for this module.
todo.txt       Things still to be done.