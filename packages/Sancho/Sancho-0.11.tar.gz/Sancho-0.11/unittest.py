"""Yet another unit testing framework for Python."""

# created 2000/03/17, Greg Ward

__revision__ = "$Id: unittest.py 22221 2003-08-15 19:38:19Z nascheme $"


import sys, string, re, pdb
from getopt import getopt
from types import *
import sets
from indented_file import IndentedFile
import traceback


def warn (msg):
    sys.stderr.write("warning: " + msg + "\n")


class TestScenario:

    def __init__ (self, options=None, outfile=None):
        self.tests_run = 0
        self.tests_ok = 0
        self.cases_ok = 1
        self.case_ok = 1

        self.options = options or TestOptions()
        self.out = outfile or IndentedFile(sys.stdout, 0, 2)
        if hasattr(self, 'description'):
            self.scenario_header = "%s (%s):\n" % (self.__class__.__name__,
                                                   self.description)
        else:
            self.scenario_header = "%s: " % self.__class__.__name__
        self.case_header = None # header for current test case
        self.printed_scenario_header = 0
        self.printed_case_header = 0


    def ensure_scenario_header(self, newline=0):
        if not self.printed_scenario_header:
            self.out.write(self.scenario_header)
            self.printed_scenario_header = 1
        if newline and self.printed_scenario_header == 1:
            self.out.write("\n")
            self.printed_scenario_header = 2


    def ensure_case_header(self, newline=0):
        self.ensure_scenario_header(newline=1)
        if not self.printed_case_header:
            self.out.write(self.case_header)
            self.printed_case_header = 1
        if newline and self.printed_case_header == 1:
            self.out.write("\n")
            self.printed_case_header = 2


    def setup (self):
        pass

    def shutdown (self):
        pass


    def _find_test_cases (self, case_names):
        """Examine the current class (ie. the class of 'self') to find
        all test cases in it -- that is, all methods whose names
        begin with 'check_'.  Returns a list of bound methods."""

        if not case_names:
            case_names = dir(self.__class__)

        cases = []
        for name in case_names:
            if name.startswith("check_"):
                method = getattr(self, name)
                if callable(method):
                    cases.append(method)
        cases.sort(lambda a, b: cmp(a.__name__, b.__name__))
        return cases


    def run (self, case_names=None):
        """Run the test cases in this test scenario.  Test cases are
        either specified by name or are found by searching for all methods
        whose names start with 'check_'.
        
        Every test case is implemented by a method of 'self'.  Those
        methods are called in turn, and the results are reported.  If an
        exception was caught from the body of the test case itself (ie.,
        not from a particular test), that is reported.  The number of
        tests run, passed, and failed is always reported."""

        cases = self._find_test_cases(case_names)
        for case in cases:
            self.run_case(case)

        results = TestResults(self.tests_run, self.tests_ok, self.cases_ok)

        if self.options.show_scenario_results:
            self.ensure_scenario_header()
            self.out.indent_more()
            self.out.write("%s\n" % results)
            self.out.indent_less()

        return results


    def run_case (self, case):
        self.case_header = "  %s: " % case.__name__
        self.printed_case_header = 0
        self.case_ok = 1
        try:
            self.setup()
            case()
        except KeyboardInterrupt:
            raise
        except:
            self.case_ok = 0
            self.ensure_case_header(newline=1)
            self.out.indent_more(4)
            traceback.print_exc(file=self.out)
            self.out.indent_less(4)
            if self.options.use_debugger:
                debugger()
        try:
            self.shutdown()
        except KeyboardInterrupt:
            pass
        except:
            self.case_ok = 0
            self.ensure_case_header(newline=1)
            self.out.indent_more(4)
            traceback.print_exc(file=self.out)
            self.out.indent_less(4)
            if self.options.use_debugger:
                debugger()
        if not self.case_ok:
            self.cases_ok = 0
        elif (self.options.show_testcase_results and
                not self.options.report_passes):
            self.ensure_case_header()
            self.out.write("ok\n")


    def report_pass (self, msg):
        self.tests_ok += 1
        if self.options.report_passes:
            self.print_report("ok", msg)


    def report_fail (self, msg, exc_info=None):
        self.case_ok = 0
        info = get_caller_info(2)
        failed_at = ["failed at %s, line %s:" % info[0:2],
                     "  " + info[3]]
        self.print_report("not ok", msg, failed_at, exc_info)


    def print_report (self, status, message, extra=None, exc_info=None):
        self.ensure_case_header(newline=1)
        self.out.indent_more(4)
        self.out.write("%s: %s\n" % (status, message))
        self.out.indent_more()
        if extra:
            for line in extra:
                self.out.write(line + "\n")
        if exc_info:
            (exc_type, exc_value, exc_tb) = exc_info
            traceback.print_exception(exc_type, exc_value, exc_tb,
                                      file=self.out)
        self.out.indent_less()
        self.out.indent_less(4)


    def test_val (self, code, value=None, match_ident=0, match_types=0):
        (globals, locals) = get_caller_env()
        self.tests_run += 1
        try:
            val = eval(code, globals, locals)
        except:
            self.report_fail("%s != %r" % (code, value), sys.exc_info())
        else:
            if match_ident:
                if val is value:
                    self.report_pass("%s is %r@%x" % (code, value, id(value)))
                else:
                    self.report_fail("%s is not %r@%x (got %r@%x)" %
                                      (code,
                                       value, id(value),
                                       val, id(val)))

            else:                       # just match on equality
                if match_types:
                    if type(value) is InstanceType:
                        if isinstance(val, value.__class__):
                            type_msg = (" (and is an instance of %s)" %
                                        value.__class__.__name__)
                            types_ok = 1
                        else:
                            type_msg = (" (type mismatch: not instance of %s)"%
                                        value.__class__.__name__)
                            types_ok = 0
                    elif type(val) is type(value):
                        type_msg = " (and types match: %s)" % type(value)
                        types_ok = 1
                    else:
                        type_msg = (" (type mismatch: expected %s, got %s)" %
                                      (type(value), type(val)))
                        types_ok = 0
                else:
                    type_msg = ""
                    types_ok = 1

                if not types_ok:
                    self.report_fail("%s != %r" % (code, value) + type_msg)
                else:
                    if val == value:
                        self.report_pass("%s == %r" % (code, value) + type_msg)
                    else:
                        self.report_fail("%s != %r (got %r)" %
                                          (code, value, val))

    # test_val ()

    # Alias for test_val()
    test = test_val

    def test_true (self, code, _level=1):
        # XXX the _level argument is a bit of a hack, needed because
        # test_bool() calls test_{true,false}(), so needs to increase
        # the stack level passed to get_caller_env() by one.  _level
        # can go away if test_bool() ever goes away.
        (globals, locals) = get_caller_env(level=_level)
        self.tests_run += 1
        try:
            val = eval(code, globals, locals)
        except:
            self.report_fail("%s not true" % code,
                             sys.exc_info())
        else:
            if val:
                self.report_pass("%s is true (%r)" % (code, val))
            else:
                self.report_fail("%s not true (got %r)" % (code, val))

    def test_false (self, code, _level=1):
        (globals, locals) = get_caller_env(level=_level)
        self.tests_run += 1
        try:
            val = eval(code, globals, locals)
        except:
            self.report_fail("%s not false" % code,
                             sys.exc_info())
        else:
            if val:
                self.report_fail("%s not false (got %r)" % (code, val))
            else:
                self.report_pass("%s is false (%r)" % (code, val))

    def test_bool (self, code, want_true=1):
        # XXX there are two disadvantages to coding test_bool() as
        # a wrapper around test_{true,false}():
        #   * test_{true,false}() need the hackish _level arg
        #   * test failure reports point to the call to
        #     test_{true,false}() here as the point-of-failure, rather
        #     than the real failure point in the test script.
        #
        # However, doing it this way should make it clear that
        # test_{true,false}() are preferred over test_bool()!
        if want_true:
            return self.test_true(code, _level=2)
        else:
            return self.test_false(code, _level=2)

    def test_set (self, code, setval):
        (globals, locals) = get_caller_env()
        self.tests_run += 1
        try:
            val = eval(code, globals, locals)
        except:
            self.report_fail("%s != %r" % (code, setval), sys.exc_info())
        else:
            if not isinstance(val, sets.BaseSet):
                val = sets.Set(val)
            if not isinstance(setval, sets.BaseSet):
                setval = sets.Set(setval)
            if val == setval:
                self.report_pass("%s == %r" % (code, setval))
            else:
                self.report_fail("%s != %r (got %r)" % (code, setval, val))
        
    def test_seq (self, code, seqval, match_types=0, match_order=1):
        (globals, locals) = get_caller_env()
        self.tests_run += 1
        try:
            val = eval(code, globals, locals)
        except:
            self.report_fail("%s != %r" % (code, seqval), sys.exc_info())
        else:

            # If match_order false, then we put the two sequence objects
            # into real lists and sort them before comparing, so that
            # differences in the ordering of elements disappear.
            if not match_order:
                try:
                    val = list(val)
                except TypeError:
                    self.report_fail("%s not a sequence (got %r)" %
                                      (code, val))
                    return

                seqval = list(seqval)
                val.sort()
                seqval.sort()

            # If match_types true, then both the type and elements of the
            # two sequences have to be the same -- ie. we can just use
            # the normal comparison operator.  (Note that "match_types
            # and match_order" is effectively the same as just calling
            # 'test_val()'.)
            if match_types:
                passed = (val == seqval)

            # Otherwise, have to compare element-by-element -- ie. do
            # just what the normal comparison operator does, but don't
            # care about the nature of the sequence objects.  Note that
            # we rely on elements of the two sequences to be equal in
            # the conventional sense -- that is, [1,2,3] and (1,2,3) are
            # equal here, as are [1,2,("foo","bar")] and (1,2,("foo","bar"))
            # -- but NOT [1,2,("foo","bar")] and (1,2,["foo","bar"]).
            else:
                if len(val) == len(seqval):
                    for i in range(len(val)):
                        if val[i] != seqval[i]:
                            passed = 0
                            break
                    else:
                        passed = 1
                else:
                    passed = 0

            # OK, we have now (possibly) reordered the two sequences and
            # then compared them.  'passed' is true if they compared OK.
            ordered = (match_order) and "(in order)" or "(ignoring order)"
            if passed:
                self.report_pass("%s == %r %s" % (code, seqval, ordered))
            else:
                self.report_fail("%s != %r %s (got %r)" %
                                 (code, seqval, ordered, val))


    def test_stmt (self, stmt):
        "Test whether the statement 'stmt' completes without problems."

        (globals, locals) = get_caller_env()
        self.tests_run += 1
        try:
            exec stmt in globals, locals
        except:
            # Raised an exception
            self.report_fail("%s" % stmt, sys.exc_info())
        else:
            # No exception raised
            self.report_pass("%s ran quietly" % (stmt))

    # test_stmt ()

    def test_exc (self, stmt, exc):
        """Test whether the statement 'stmt' raises the expected exception."""

        (globals, locals) = get_caller_env()
        self.tests_run += 1
        try:
            exec stmt in globals, locals
        except:
            exc_info = sys.exc_info()
            (exc_seen, exc_value, exc_tb) = exc_info
            if issubclass(exc_seen, exc):  # good, got the expected exception
                self.report_pass \
                    ("%s raised %s" % (stmt, describe_exc(exc_info)))

            else:                       # exception, but not the expected one
                self.report_fail \
                    ("%s didn't raise %s" % (stmt, exception_name (exc)),
                     exc_info)
            return exc_value
        else:
            self.report_fail \
                ("%s didn't raise %s" % 
                 (stmt, exception_name(exc)))
            return None

    # test_exc ()

    def test_type (self, code, typ=None, match_types=0):
        "Test whether the value returned by 'code' is of the specified type."

        (globals, locals) = get_caller_env()
        self.tests_run += 1
        try:
            val = eval(code, globals, locals)
        except:
            self.report_fail("%s not of type %s" % (code, typ), sys.exc_info())
        else:
            if type(val) is InstanceType:
                val_type = val.__class__
            else:
                val_type = type(val)

            if match_types:
                if val_type is typ:
                    self.report_pass("%s returned object of type %s" %
                                     (code, typ))
                else:
                    self.report_fail("%s type mismatch: "
                                     "returned object of type %s, not %s"
                                     % (code, val_type, typ))

            else:
                if isinstance(val, typ):
                    self.report_pass("%s returned object of type %s" %
                                     (code, typ))
                else:
                    self.report_fail("%s type mismatch: "
                                     "returned object of type %s, not %s"
                                     % (code, val_type, typ))
    # test_type ()


class TestOptions:
    """Contains the options that control the output and verbosity of
    running a test scenario.  This class exists purely as a holder for
    instance attributes:

    Instance attributes:
      report_passes: boolean
        print a line for each individual test that passes
      show_testcase_results: boolean
        print a line for each check method that runs
      show_scenario_results: boolean
        print a line for each scenario that runs
      show_overall_results: boolean
        print a line after running all the scenarios summarizing the results

    """

    # verbosity levels
    LOW = 0
    MEDIUM = 1                              # the default
    HIGH = 2

    def __init__ (self, verbosity=MEDIUM, show_coverage=0, use_debugger=0):

        self.show_coverage = show_coverage
        self.show_coverage_lines = 0
        self.use_debugger = use_debugger

        if verbosity == TestOptions.LOW:
            self.report_passes = 0
            self.show_testcase_results = 0
            self.show_scenario_results = 0
            self.show_overall_results = 1

        elif verbosity == TestOptions.MEDIUM:
            self.report_passes = 0
            self.show_testcase_results = 0
            self.show_scenario_results = 0
            self.show_overall_results = 1

        elif verbosity == TestOptions.HIGH:
            self.report_passes = 1
            self.show_testcase_results = 1
            self.show_scenario_results = 1
            self.show_overall_results = 1
            if self.show_coverage:
                self.show_coverage_lines = 1


class TestResults:

    def __init__(self, total_run=0, total_ok=0, cases_ok=1):
        self.total_run = total_run
        self.total_ok = total_ok
        self.cases_ok = cases_ok

    def ok(self):
        return (self.total_run == self.total_ok and self.cases_ok)

    def __add__(self, other):
        return TestResults(self.total_run + other.total_run,
                           self.total_ok + other.total_ok,
                           self.cases_ok and other.cases_ok)

    def __str__(self):
        if self.ok():
            return "%d tests passed" % self.total_run
        else:
            failed = self.total_run - self.total_ok
            return "%d tests run, %s failed" % (self.total_run, failed)

    def format(self, tag=""):
        if self.ok():
            s = "ok"
        else:
            s = "not ok"
        if tag:
            s += " %s" % tag
        return "%s: %s" % (s, self)


def exception_name (exc):
    """Returns the name of an exception without any package or module
    names cluttering it up.  'exc' must be a string or exception
    class)."""
    if type(exc) is ClassType:
        return exc.__name__
    else:
        return exc


def describe_exc (exc_info):
    exc_type, exc_value, exc_tb = exc_info
    return "%s: \"%s\"" % (exception_name (exc_type), exc_value)


def get_caller_env (level=1):
    """get_caller_env(level : int = 1) -> (globals : dict, locals : dict)

    Return the environment of a caller: its dictionaries of global and
    local variables.  'level' has same meaning as for '_getframe()'.
    """
    frame = sys._getframe(level+1)
    return (frame.f_globals, frame.f_locals)


def get_frame_info (frame):
    """get_frame_info(frame)
       -> (filename : string,
           lineno : int,
           function_name : string,
           code_line : string)

    Extracts and returns a tuple of handy information from an execution
    frame.
    """
    import linecache
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    function_name = frame.f_code.co_name
    code_line = string.strip(linecache.getline(filename, lineno))

    return (filename, lineno, function_name, code_line)


def get_caller_info (level=1):
    """get_caller_info(level : int = 1)
       -> (filename : string,
           lineno : int,
           function_name : string,
           code_line : string)

    Extracts and returns a tuple of handy information from some caller's
    execution frame.  'level' is the same as for '_getframe()', i.e.  if
    level is 1 (the default), gets this information about the caller of
    the function that is calling 'get_caller_info()'.
    """
    return get_frame_info(sys._getframe(level+1))


def run_scenarios (scenarios, options=None, module=None):
    """Run a bunch of test scenarios.  'scenarios' is a list of test
    scenario descriptions.  A test scenario description is either a
    single class object, in which case all test cases in that test
    scenario are run; or it is a tuple (test_scenario, [case1, case2,
    ...])  where 'test_scenario' is again a class object and 'case1'
    etc.  are the names of the test cases to run.  Test case names are
    the same as the method that implements the test case, with the
    leading "check_" optionally lopped off."""

    if options is None:
        options = TestOptions(verbosity, show_coverage=show_coverage,
                              use_debugger=use_debugger)

    if module is None:
        module = sys.modules['__main__']
        
    if not scenarios:
        scenarios = find_scenarios(module)

    out = IndentedFile(sys.stdout, 0, 2)

    if options.show_coverage:
        module_dict = vars(module)
        tested_modules = module_dict.get('tested_modules')
        if tested_modules:
            from code_coverage import Coverage
            coverage = Coverage(modules=tested_modules)
            sys.settrace(coverage.trace)

    # loop over the list of test scenarios and run them
    results = TestResults()
    for scenario in scenarios:
        if isinstance(scenario, ClassType):
            klass = scenario
            case_names = None
        elif isinstance(scenario, TupleType) and len(scenario) == 2:
            (klass, case_names) = scenario
        else:
            raise TypeError, \
                  "every element in 'scenarios' must be either a " + \
                  "class object or 2-tuple: '%r' invalid" % scenario

        scenario_inst = klass(options, outfile=out)
        if not isinstance(scenario_inst, TestScenario):
            raise TypeError, \
                 "test scenario classes must be subclasses of TestScenario: "+\
                 "%s invalid" % klass.__name__

        results += scenario_inst.run(case_names)

    if options.show_coverage:
        if tested_modules is None:
            out.write('Coverage analysis requested but '
                      '"tested_modules" not defined\n')
        else:
            # reload tested modules to get coverage of imports, etc.
            for name in tested_modules:
                module = sys.modules.get(name)
                if module:
                    reload(module)
            sys.settrace(None)
            out.write("code coverage:\n")
            out.indent_more()
            coverage.write_results(out, show_lines=options.show_coverage_lines)
            out.indent_less()

    if options.show_overall_results:
        out.write("%s\n" % results.format())

    return results

# run_scenarios ()


def find_test_scenario (script, name, module=None):

    if module is None:
        module = sys.modules['__main__']
    module_dict = vars(module)

    if name[-4:] != "Test":
        try_names = [name, name + "Test"]
    else:
        try_names = [name]

    for try_name in try_names:
        klass = module_dict.get(try_name)
        if klass:
            break
    else:
        if len (try_names) == 1:
            reason = "'%s' class not found" % try_names[0]
        elif len (try_names) == 2:
            reason = "neither '%s' nor '%s' classes found" % tuple(try_names)
        else:
            raise RuntimeError, "this can't happen!"

        raise ValueError, \
              ("unknown test scenario '%s': " + reason +
               " in script %s") % \
              (name, script)

    if not issubclass (klass, TestScenario):
        raise RuntimeError, \
              ("bad test scenario '%s': " +
               "'%s' not a subclass of TestScenario") % \
              (name, name)

    return klass

# find_test_scenario()
    

def find_scenarios (module):
    """Finds all test scenarios (subclasses of TestScenario) made available
    by module 'module' and returns the list of class objects found.
    "Available" means "listed in the module global variable
    'test_scenarios' if it is defined, or defined in that module if
    not"."""

    if hasattr(module, 'test_scenarios'):
        scenarios = module.test_scenarios
    else:
        scenarios = []
        mod_dict = vars(module)
        for val in mod_dict.values():
            if (isinstance(val, ClassType) and
                    issubclass(val, TestScenario) and
                    val.__module__ == module.__name__):
                scenarios.append(val)
    return scenarios


def has_test_case (scenario, casename):
    if hasattr (scenario, casename):
        return casename
    elif casename[0:6] != "check_" and hasattr (scenario, "check_" + casename):
        return "check_" + casename
    else:
        return None


def parse_args (argv=sys.argv):
    """Parse the command-line arguments to a test script.
    Syntax is:
      [-c] [-q|-v] [scenario1][:case1,...] ...
    ie. user may specify any number of test scenarios and any number
    of test cases for each scenario.  Scenarios are specified by the
    name of the class that implements them, and cases by the name
    of the method.  Trailing "Test" is optional for scenario names,
    as is leading "check_" for case names.

    If no scenarios or cases are supplied, all found in the test script
    (__main__ module) are run.  If a scenario is specified without any test
    cases, all cases ("check_" methods or methods listed in class attribute
    'test_cases') are run.  If a test case is specified without any test
    scenario, that test case is run in all test scenarios (this is mainly a
    shortcut for scripts with a single test scenario class).

    Exits with appropriate error message and non-zero exit status if any
    errors found in command-line.  Exits with help message and zero exit
    status if "-h" or "--help" seen on command-line.

    Returns a tuple (scenarios, options); 'options' is a TestOptions
    instance recording the -q/-v/etc. options; scenarios is a list
    of test scenario descriptions as required by 'run_scenarios()'."""

    script = sys.argv[0]
    args = sys.argv[1:]
    usage = "usage: %s: [-c] [-i] [-q] [-v]" % script

    # Check for help options
    if "-h" in sys.argv or "--help" in sys.argv:
        print usage
        sys.exit()

    # Look for -q and -v; modify default option settings appropriately
    (opts, args) = getopt(args, 'cqvi')
    verbosity = TestOptions.MEDIUM
    show_coverage = 0
    use_debugger = 0
    for (opt,_) in opts:
        if opt == '-i':
            use_debugger = 1
        if opt == '-c':
            show_coverage = 1
        elif opt == '-q':
            verbosity = TestOptions.LOW
        elif opt == '-v':
            verbosity = TestOptions.HIGH
    options = TestOptions(verbosity, show_coverage=show_coverage,
                          use_debugger=use_debugger)

    all_scenarios = find_scenarios (sys.modules['__main__'])

    # No arguments -- we'll just run all tests
    if not args:
        return (all_scenarios, options)

    scenarios = []
    for arg in args:

        colon = string.find (arg, ':')

        # No colon in 'arg' -- it's just a bare word.
        if colon == -1:

            # Special case for lazy typists running test scripts that only
            # define one test scenario: a lone word on the command line is
            # first checked to see if it's the name of a test case (method)
            # in that test scenario.
            if len(all_scenarios) == 1:
                casename = has_test_case (all_scenarios[0], arg)
                if casename:
                    scenarios.append ((all_scenarios[0],[casename]))
                    continue

            # Otherwise, assume the lone word is the name of a test
            # scenario class; dig up and validate the class object.
            klass = find_test_scenario (script, arg)
            scenarios.append (klass)

        # Found a colon: split into scenario name and list of test cases.
        else:
            scenario = arg[:colon]
            klass = find_test_scenario (script, scenario)

            # If no cases were listed (ie. there's nothing after the
            # colon), then treat this like the no-colon case above: will
            # run all test cases
            if colon+1 == len(arg):
                scenarios.append (klass)

            # Otherwise, pull out the list of case names after the colon
            else:
                cases = string.split (arg[colon+1:], ',')
                scenarios.append ((klass, cases))

    return (scenarios, options)


def debugger ():
    t = sys.exc_info()[2]
    while (t.tb_next is not None and
           t.tb_next.tb_next is not None and
           t.tb_next.tb_next.tb_next is not None):
        t = t.tb_next
    p = pdb.Pdb()
    p.reset()
    p.interaction(t.tb_frame, t)
