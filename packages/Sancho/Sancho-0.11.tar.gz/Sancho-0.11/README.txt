Sancho
------

Sancho contains the unit test module that we use at the MEMS Exchange.
Among the features it supports are:

      * Simple and relatively straightforward to use
      * Several different test functions: test_stmt, test_val, test_type, etc.
      * Optionally displays the code coverage of a test suite
      * Script for running all test suites in a directory tree

Note that the code in sancho/unittest.py is fairly repetitive, and
badly needs to be refactored and tidied up.  This might require
changing the public interface for Sancho.  We're not sure when this
refactoring will happen, so just be aware that a future version of
Sancho might modify its interface, meaning that you'd have to adjust
your test cases.

(For a while this code was included in the Quixote distribution as the
quixote.test package, but was never actually used or documented while
it resided there.)


INSTALLATION
------------

Just run 'python setup.py install'.


TRYING IT OUT
-------------
After Sancho has been installed, try running 'python examples/test_simple.py'.
You should get the following output:

$ python examples/test_simple.py
MyFunctionTest: 
  check_func: ok
  check_val_param: ok
  9 tests passed
ok: 9 tests passed

Adding the -v switch will produce more verbose output, listing each
test case as it's performed, and adding -c will measure the lines of
code covered.  Adding both -c and -v will produce a listing of the
tested module, with execution counts for each lines and untested lines
highlighted:

$ python examples/test_simple.py -v -c
MyFunctionTest: 
  check_func: 
    ok: simple.f('', 0) == ''
    ok: simple.f('abc', 0) == ''
    ok: simple.f('', 1) == ''
    ok: simple.f('abc', 1) == 'abc'
    ok: simple.f('', 3) == ''
    ok: simple.f('abc', 3) == 'abcabcabc'
  check_val_param: 
    ok: simple.f('', -1) raised ValueError: "val cannot be negative"
    ok: simple.f('', 0) ran quietly
    ok: simple.f('', 1) ran quietly
  9 tests passed
code coverage:
  simple: 
      . # This is a trivial Python module, containing a single function f().
      . 
     10: def f(s, val):
      9:     if val < 0:
      1:         raise ValueError, 'val cannot be negative'
      8:     elif val == 42:
  >>>>>>         print 'The answer!'
      .  
      8:     return s * val
  83.3% (5/6)
ok: 9 tests passed


AUTHOR, COPYRIGHT, LICENSE, AVAILABILITY
----------------------------------------

Greg Ward wrote the original version of Sancho, and its design was
inspired by Kent Beck's Smalltalk testing framework.  Neil Schemenauer
added code coverage features using a modified version of Skip
Montanaro's trace.py.  It was packaged for release for 

Copyright (c) 2001 Corporation for National Research Initiatives.
All Rights Reserved.

See LICENSE.txt for license information.

For the latest version, visit
  http://www.mems-exchange.org/software/sancho/

There's no mailing list just for Sancho, but you can ask questions and
discuss issues about Sancho on the Quixote mailing list:
        http://www.mems-exchange.org/mailman/listinfo/quixote-users/


$Id: README.txt 22717 2003-10-09 15:57:56Z nascheme $
