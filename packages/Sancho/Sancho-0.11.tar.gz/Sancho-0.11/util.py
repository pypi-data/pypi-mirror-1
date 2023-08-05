"""sancho.util

   Sancho test utility functions

   Helper functions used to run a single test or multiple tests recursively
   For example, run all tests found in and below the current directory:
   
   >>> print run_all_scripts(find_test_scripts('.'))

"""

__revision__ = "$Id: util.py 20440 2003-01-24 22:38:10Z dbinger $"

import sys, os, re
import new

from sancho.unittest import TestOptions, TestResults, \
        find_scenarios, run_scenarios

def find_test_scripts (start_dir):
    """(start_dir : str) -> [str]

       Recursively explore from 'start_dir', looking for all
       "test/test_*.py" files.  Return the list of matches.
    """

    filename_re = re.compile('^test_\w+\.py$')

    def visit (matches, dirname, names, filename_re=filename_re):
        if os.path.basename(dirname) == 'test':
            for name in names:
                if filename_re.match(name):
                    name = os.path.normpath(os.path.join(dirname, name))
                    matches.append(name)

    matches = []
    os.path.walk(start_dir, visit, matches)
    matches.sort()
    return matches


def run_test_script (script, use_debugger=0, verbosity=1, show_coverage=0): 
    """(script : str,
        use_debugger : boolean=0,
        verbosity : int=1,
        show_coverage : boolean=0)
       -> TestResults

       Run all the tests in file 'script', capture and return results.
    """
    # XXX should catch exceptions from execfile here, but that would
    # mean duplicating logic from TestScenario.run(); I'll wait 'till I
    # have a decent "test collection" abstraction and just do it once.

    test_name = os.path.splitext(os.path.basename(script))[0]
    test_directory = os.path.dirname(script)
    if test_directory and test_directory not in sys.path:
        sys.path = [test_directory] + sys.path
    else:
        test_directory = None
    test_mod = new.module(test_name)
    test_mod.__file__ = script + " (fake)"
    execfile(script, test_mod.__dict__)
    scenarios = find_scenarios(test_mod)

    options = TestOptions(verbosity=verbosity,
                          show_coverage=show_coverage,
                          use_debugger=use_debugger)
    options.show_overall_results = 0
    if verbosity > TestOptions.LOW:
        sys.stdout.write("%s " % script)
    results = run_scenarios(scenarios, options, module=test_mod)
    if test_directory and sys.path[0] == test_directory:
        sys.path = sys.path[1:]
    if verbosity > TestOptions.LOW:
        sys.stdout.write("%s\n" % results)
    return results

def run_all_scripts (scripts, use_debugger=1, show_coverage=0, verbosity=0):
    """(scripts : [str], use_debugger : boolean, verbosity : int)
        -> TestResults

        Run all the test scripts in 'scripts', capture and return results.
    """
    results = TestResults()
    for script in scripts:
        results += run_test_script(script,
                                   use_debugger=use_debugger,
                                   verbosity=verbosity,
                                   show_coverage=show_coverage)
    return results


