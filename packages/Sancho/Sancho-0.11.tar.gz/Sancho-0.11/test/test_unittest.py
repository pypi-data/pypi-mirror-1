#!/usr/bin/env python

# A test suite for the test suite program; my brain hurts...
# This test suite creates a DummyTest class, and then tries to
# exercise all the success and failure cases.  After exercising
# a set of cases, the only check is that the test cases either
# all failed or all succeeded.  If there's a mismatch, uncomment
# the final 'run_scenario (DummyTest)' line and visually inspect the output
# to determine which test is wrong.

# created 2000/03/27, A.M. Kuchling

__revision__ = "$Id: test_unittest.py 20227 2003-01-16 21:26:56Z akuchlin $"

from sancho.unittest import TestScenario, parse_args, run_scenarios

tested_modules = [ "sancho.unittest" ]

# for testing test_val's ability to discern type compatibility of instances
class Foo:
    def __cmp__ (self, other):
        return 0
    
class SubFoo (Foo):
    pass

class Bar:
    pass

# For 2.2, create new-style classes
try:
    object
except NameError:
    class object: pass

class NewFoo(object):
    def __cmp__ (self, other):
        return 0
    
class NewSubFoo (NewFoo):
    pass

class NewBar(object):
    pass
    
class DummyTest(TestScenario):
    "Class used as the test bed for exercising unittest.py"

    # The real test scenario class is UnittestTest, found after
    # this class.

    def print_report(self, *args):
        pass # throw away output
    
    def setup(self):
        pass

    def shutdown(self):
        pass

    test_cases = []
    for thing in ('val', 'bool', 'stmt', 'exc', 'type'):
        test_cases.append ('check_test_%s_success' % thing)
        test_cases.append ('check_test_%s_failure' % thing)

    def check_test_val_success(self):
        "Verify the test_val() method (success)"
        self.test_val( 'self.return_value(2)', 2)
        s = "foo"
        self.test_val( 'self.return_value(s)', s, match_ident=1)
        self.test_val( 'self.return_value([1,2])', [1,2], match_types=1)
        self.test_val( 'self.return_value(2L)', 2)

        self.test_val('Foo()', Foo(), match_types=1)
        self.test_val('SubFoo()', Foo(), match_types=1)
        self.test_val('NewFoo()', NewFoo(), match_types=1)
        self.test_val('NewSubFoo()', NewFoo(), match_types=0)
        

    def check_test_val_failure(self):
        "Verify the test_val() method (failure)"
        self.test_val( 'self.return_value(0)', 1)
        self.test_val( 'self.raise_exception(ValueError)', 1)
        self.test_val( 'self.return_value("foo"+"bar")', "foobar",
                       match_ident=1)
        self.test_val( 'self.return_value(2L)', 2, match_types=1)

        self.test_val('Foo()', SubFoo(), match_types=1)
        self.test_val('Foo()', Bar(), match_types=1)

    def check_test_bool_success(self):
        "Verify the test_bool() method (success)"
        # Success cases: exercise the various flavours of truth and
        # falsehood in Python
        self.test_bool('1')
        self.test_bool('0', want_true=0)
        self.test_bool('None', want_true=0)
        self.test_bool('"foo!"', want_true=1)
        self.test_bool('""', want_true=0)
        self.test_bool('[1]')
        self.test_bool('[]', want_true=0)
        self.test_bool('(0,)')
        self.test_bool('()', want_true=0)
        self.test_bool('{1:1}')
        self.test_bool('{}', want_true=0)
        self.test_bool('self')
        self.test_bool('self.check_test_bool_success')
        self.test_bool('DummyTest')
        

    def check_test_bool_failure(self):
        "Verify the test_bool() method (failure)"
        # Two failure cases that don't raise an exception
        self.test_bool('self.return_value(1)', want_true=0)
        self.test_bool('self.return_value(0)', want_true=1)
        self.test_bool('None')
        self.test_bool('{0:0}', want_true=0)
        
        # Two failure cases that raise an exception
        self.test_bool( 'self.raise_exception(ValueError)', 0)
        self.test_bool( 'self.raise_exception(ValueError)', 1)

    def check_test_stmt_success(self):
        "Verify the test_stmt() method (success)"
        # Success
        self.test_stmt( 'self.return_value( (1.0, 2, "abc") )')

    def check_test_stmt_failure(self):
        "Verify the test_stmt() method (failure)"
        # Failure
        self.test_stmt( 'self.raise_exception(ValueError)')

    def check_test_exc_success(self):
        "Verify the test_exc() method (success)"
        # Success cases
        exc = self.test_exc( 'self.raise_exception(ValueError)', ValueError)
        self.test_bool( 'isinstance(exc, ValueError)')

        exc = self.test_exc( 'self.raise_exception(ValueError, "foo!")',
                             ValueError)
        self.test_bool( 'isinstance(exc, ValueError) and str(exc) == "foo!"')

    def check_test_exc_failure(self):
        "Verify the test_exc() method (failure)"

        # Failure case: wrong exception was raised
        self.test_exc( 'self.raise_exception(ValueError)', TypeError)

        # Failure case: no exception was raised
        self.test_exc( 'self.return_value( 1 )', TypeError)

    def check_test_type_success (self):
        "Verify the test_type() method (success)"
        # Success cases
        self.test_type('SubFoo()', Foo, match_types=0)
        self.test_type('NewSubFoo()', NewFoo, match_types=0)
        self.test_type('Foo()', Foo, match_types=1)
        self.test_type('NewFoo()', NewFoo, match_types=1)
        self.test_type('1', type(1), match_types=0)
        
    def check_test_type_failure (self):
        "Verify the test_type() method (failure)"
        # Failure cases
        # Exact matches that fail
        self.test_type('SubFoo()', Foo, match_types=1)
        self.test_type('NewSubFoo()', NewFoo, match_types=1)
        # Classes that aren't related
        self.test_type('Bar()', Foo)
        self.test_type('NewBar()', NewFoo)
        # Simple types that don't match
        self.test_type('1', type(""))
        # Raised an exception
        self.test_type('1/0', type(1))
        
    # XXX this one isn't automatically tested in UnittestTest below,
    # since there's no framework for examining the output of test cases
    # that actually blow up themselves.  Hmmm.

    #def check_blowup(self):
    #    "Check when the test case itself blows up"
    #    self.test_val("1")
    #    raise RuntimeError, "aiieee!!!"
    #    self.test_val("1")

    def return_value(self, value):
        return value
        
    def raise_exception(self, exc, args=None):
        if args is not None:
            raise exc, args
        else:
            raise exc

class UnittestTest(TestScenario):
    def setup(self):
        self.scenario = DummyTest()
        #self.scenario.run()

    def shutdown(self):
        del self.scenario

    def check_test_val_success(self):
        "Verify the success cases of the test_val() method"
        self.scenario.check_test_val_success()
        self.test_val('(self.scenario.tests_run, self.scenario.tests_ok)',
                      (8, 8))

    def check_test_val_failure(self):
        "Verify the failure cases of the test_val() method"
        self.scenario.check_test_val_failure()
        self.test_val('(self.scenario.tests_run, self.scenario.tests_ok)',
                      (6, 0))

    def check_test_bool_success(self):
        "Verify the success cases of the test_bool() method"
        self.scenario.check_test_bool_success()
        self.test_val('(self.scenario.tests_run, self.scenario.tests_ok)',
                      (14, 14))
        
    def check_test_bool_failure(self):
        "Verify the failure cases of the test_bool() method"
        self.scenario.check_test_bool_failure()
        self.test_val('(self.scenario.tests_run, self.scenario.tests_ok)',
                      (6, 0))

    def check_test_stmt_success(self):
        "Verify the success cases of the test_stmt() method"
        self.scenario.check_test_stmt_success()
        self.test_val('(self.scenario.tests_run, self.scenario.tests_ok)',
                      (1, 1))
        
    def check_test_stmt_failure(self):
        "Verify the failure cases of the test_stmt() method"
        self.scenario.check_test_stmt_failure()
        self.test_val('(self.scenario.tests_run, self.scenario.tests_ok)',
                      (1, 0))

    def check_test_exc_success(self):
        "Verify the success cases of the test_exc() method"
        self.scenario.check_test_exc_success()
        self.test_val('(self.scenario.tests_run, self.scenario.tests_ok)',
                      (4, 4))

    def check_test_exc_failure(self):
        "Verify the failure cases of the test_exc() method"
        self.scenario.check_test_exc_failure()
        self.test_val('(self.scenario.tests_run, self.scenario.tests_ok)',
                      (2, 0))

    def check_test_type_success (self):
        "Verify the success cases of the test_type() method"
        self.scenario.check_test_type_success()
        self.test_val('(self.scenario.tests_run, self.scenario.tests_ok)',
                      (5, 5))

    def check_test_type_failure (self):
        "Verify the failure cases of the test_type() method"
        self.scenario.check_test_type_failure()
        self.test_val('(self.scenario.tests_run, self.scenario.tests_ok)',
                      (6, 0))

test_scenarios = [UnittestTest]

if __name__ == "__main__":
    (scenarios, options) = parse_args()
    run_scenarios (scenarios, options)
