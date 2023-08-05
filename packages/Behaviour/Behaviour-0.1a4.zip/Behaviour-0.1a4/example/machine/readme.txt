Machine Example
---------------

This is the same example as used in "Behaviour-Driven Testing with RSpec" by
Bruce Tate, translated from RSpec (Ruby) to Behaviour (Python). The original
article may be found at http://www.ibm.com/developerworks/web/library/wa-rspec/.

Listing 10 differs as it is impossible to get the specification to fail due to
some appallingly bad design in Python (in my view a client module should *NEVER*
be able to create new data elements -- this is reverting back to the bad old days
of COBOL and FORTRAN).

Ditto for Listing 15.

Note that I renamed the behaviours to get them to work with nose and pinocchio
for listing 23.