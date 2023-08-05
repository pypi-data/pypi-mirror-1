from sancho.unittest import TestScenario, parse_args, run_scenarios

import simple

tested_modules = ['simple']

class MyFunctionTest (TestScenario):

    def setup(self):
        pass

    def shutdown(self):
        pass

    def check_val_param(self):
        # Negative number should raise a ValueError
        self.test_exc("simple.f('', -1)", ValueError)

        # Zero is OK
        self.test_stmt("simple.f('', 0)")

        # Positive numbers are also OK
        self.test_stmt("simple.f('', 1)")

    def check_func(self):
        # Test the null case (val == 0)
        self.test_val("simple.f('', 0)", '')
        self.test_val("simple.f('abc', 0)", '')

        # Test the identity (val == 1)
        self.test_val("simple.f('', 1)", '')
        self.test_val("simple.f('abc', 1)", 'abc')

        # Test a real case (val == 3)
        self.test_val("simple.f('', 3)", '')
        self.test_val("simple.f('abc', 3)", 'abcabcabc')


if __name__ == "__main__":
    (scenarios, options) = parse_args()
    run_scenarios(scenarios, options)
