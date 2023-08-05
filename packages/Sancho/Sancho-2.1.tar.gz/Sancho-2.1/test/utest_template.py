#!/usr/bin/env python 
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/sancho/test/utest_template.py $
$Id: utest_template.py 25080 2004-09-13 13:41:40Z dbinger $
"""

from sancho.utest import UTest

class Test(UTest):

    def _pre(self):
        """Setup code for each test method."""

    def _post(self):
        """Shutdown code for each test method."""

    def basic(self):
        """A test method
        Output to stdout is trapped, unless an exception is raised here.
        """

if __name__ == '__main__':
    Test()
