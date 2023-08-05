Sancho
------

Sancho contains the lean unit test module that we use at the MEMS Exchange.

Sancho 2.1 runs tests, and provides output for tests that fail.

Sancho 2.1 does not count tests passed or failed.  The target is
projects that do not maintain failing tests.

Note that version 2.1 of sancho will not run tests written for earlier
versions of sancho.  The 2.1 distribution does, however, provide a 
'convert.py' script to semi-automate the conversion of tests written
for earlier versions of sancho. 

INSTALLATION
------------

Just run 'python setup.py install'.


USAGE
-----

The pattern we follow is to write unittests in separate python files
whose names all start with 'utest_'.  Each script has one or more
subclasses of sancho.utest.UTest defined, and the script ends 
by calling the constructors of each of these classes.

The UTest constructor runs every method method of the subclass (except
for those whose names start with '_') as a test.  Any test that raises
any exception will cause output, but other output from tests is 
suppressed.  If all tests in a class have common setup and 
shutdown code, you can put these in '_pre' and '_post' methods and
the UTest will call them before and after each test.

You can run the tests directly or use the included 'urun.py'
program to run all of the 'utest_' scripts below the current
directory.



AUTHOR, COPYRIGHT, LICENSE, AVAILABILITY
----------------------------------------

Copyright (c) 2005 Corporation for National Research Initiatives.
All Rights Reserved.

See LICENSE.txt for license information.

For the latest version, visit
  http://www.mems-exchange.org/software/sancho/

There's no mailing list just for Sancho, but you can ask questions and
discuss issues about Sancho on the Quixote mailing list:
        http://www.mems-exchange.org/mailman/listinfo/quixote-users/


