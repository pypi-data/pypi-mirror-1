#!/usr/bin/env python 
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/sancho/test/utest_utest.py $
$Id: utest_utest.py 25080 2004-09-13 13:41:40Z dbinger $
"""

from sancho.utest import UTest

class Test(UTest):

    def basic(self):
        print 'starting basic'
        Test._pre_count = 0
        Test._post_count = 0
        Test.a_count = 0
        Test._helper_count = 0
        class A(UTest):
            def _pre(self):
                Test._pre_count += 1
            def _post(self):
                Test._post_count += 1
            def a(self):
                Test.a_count += 1
            def _helper(self):
                Test._helper_count += 1
        A()
        assert Test._pre_count == 1
        assert Test._post_count == 1
        assert Test.a_count == 1
        assert Test._helper_count == 0


if __name__ == '__main__':
    Test()

