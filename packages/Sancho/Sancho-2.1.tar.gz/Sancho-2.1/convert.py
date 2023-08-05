#!/www/python/bin/python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/sancho/convert.py $
$Id: convert.py 25081 2004-09-13 13:48:12Z dbinger $

This script is designed to assist in the conversion of
the pre-2.0 Sancho unittest scripts into the new
Sancho utest format.  Some additional hand editing of
the output may be required, but this takes care of the
simple patterns.
"""

import re
import sys

def test_val(line, write,
             pattern=re.compile("(?P<indentation>\s*)"
                                "(?P<function_call>self.test_val)"
                                "(\()"
                                "(?P<quote>['\"])"
                                "(?P<arg1>.*)"
                                "(?P=quote),"
                                "\s*(?P<arg2>.*)"
                                "(\))"
                                )):
    match = pattern.match(line)
    if not match:
        return False
    write("%sassert %s == %s\n" % (match.group('indentation'),
                                   match.group('arg1'),
                                   match.group('arg2')))
    return True

def test_seq(line, write,
             pattern=re.compile("(?P<indentation>\s*)"
                                "(?P<function_call>self.test_seq)"
                                "(\()"
                                "(?P<quote>['\"])"
                                "(?P<arg1>.*)"
                                "(?P=quote),"
                                "\s*(?P<arg2>.*)"
                                "(\))"
                                )):
    match = pattern.match(line)
    if not match:
        return False
    write("%sassert %s == %s\n" % (match.group('indentation'),
                                               match.group('arg1'),
                                               match.group('arg2')))
    return True

def test_set(line, write,
             pattern=re.compile("(?P<indentation>\s*)"
                                "(?P<function_call>self.test_set)"
                                "(\()"
                                "(?P<quote>['\"])"
                                "(?P<arg1>.*)"
                                "(?P=quote),"
                                "\s*(?P<arg2>.*)"
                                "(\))"
                                )):
    match = pattern.match(line)
    if not match:
        return False
    write("%sassert Set(%s) == Set(%s)\n" % (match.group('indentation'),
                                             match.group('arg1'),
                                             match.group('arg2')))
    return True


def test_stmt(line, write,
              pattern=re.compile("(?P<indentation>\s*)"
                                 "(?P<function_call>self.test_stmt)"
                                 "(\()"
                                 "(?P<quote>['\"])"
                                 "(?P<arg1>.*)"
                                 "(?P=quote)"
                                 "(\))"
                                 )):
    match = pattern.match(line)
    if not match:
        return False
    write("%s%s\n" % (match.group('indentation'), match.group('arg1')))
    return True

def test_true(line, write,
              pattern=re.compile("(?P<indentation>\s*)"
                                 "(?P<function_call>self.test_true)"
                                 "(\()"
                                 "(?P<quote>['\"])"
                                 "(?P<arg1>.*)"
                                 "(?P=quote)"
                                 "(\))"
                                 )):
    match = pattern.match(line)
    if not match:
        return False
    write("%sassert %s\n" % (match.group('indentation'),
                             match.group('arg1')))
    return True

def test_bool_true(line, write,
                   pattern=re.compile("(?P<indentation>\s*)"
                                      "(?P<function_call>self.test_bool)"
                                      "(\()"
                                      "(?P<quote>['\"])"
                                      "(?P<arg1>.*)"
                                      "(?P=quote)"
                                      "(\))"
                                      )):
    match = pattern.match(line)
    if not match:
        return False
    write("%sassert %s\n" % (match.group('indentation'),
                             match.group('arg1')))
    return True


def test_false(line, write,
               pattern=re.compile("(?P<indentation>\s*)"
                                  "(?P<function_call>self.test_false)"
                                  "(\()"
                                  "(?P<quote>['\"])"
                                  "(?P<arg1>.*)"
                                  "(?P=quote)"
                                  "(\))"
                                  )):
    match = pattern.match(line)
    if not match:
        return False
    write("%sassert not %s\n" % (match.group('indentation'),
                                 match.group('arg1')))
    return True

def test_exc(line, write,
             pattern=re.compile("(?P<indentation>\s*)"
                                "(?P<function_call>self.test_exc)"
                                "(\()"
                                "(?P<quote>['\"])"
                                "(?P<arg1>.*)"
                                "(?P=quote),"
                                "\s*(?P<arg2>.*)"
                                "(\))"
                                )):
    match = pattern.match(line)
    if not match:
        return False
    write(("%stry:\n"
           "%s    %s\n"
           "%s    assert 0\n"
           "%sexcept %s: pass\n") % (
        match.group('indentation'),
        match.group('indentation'),
        match.group('arg1'),
        match.group('indentation'),
        match.group('indentation'),
        match.group('arg2')))
    return True

def run_scenarios(line, write,
                  pattern=re.compile("(?P<indentation>\s*)run_scenarios")):

    match = pattern.match(line)
    if not match:
        return False
    for test in TESTS:
        write("%s%s()\n" % (match.group('indentation'),
                            test))
    return True

TESTS = []

def class_testscenario(line, write,
                       pattern=re.compile("class "
                                          "(?P<class_name>\S+)"
                                          "\s?\("
                                          "(TestScenario)"
                                          "\):"
                                          )):
    match = pattern.match(line)
    if not match:
        return False
    write("class %s (UTest):\n" % match.group('class_name'))
    global TESTS
    TESTS.append(match.group('class_name'))
    return True

def parse_args(line, write,
               pattern=re.compile("\s*\(scenarios, options\)")):
    if pattern.match(line):
        return True
    else:
        return False

def coverage_line(line, write,
                  pattern=re.compile("\s*\options.show_coverage")):
    if pattern.match(line):
        return True
    else:
        return False

def from_sancho(line, write, pattern=re.compile("from sancho")):
    if pattern.match(line):
        write("from sancho.utest import UTest\n")
        return True
    else:
        return False

def tested_modules(line, write, pattern=re.compile("tested_modules")):
    if pattern.match(line):
        return True
    else:
        return False

def test_cases(line, write, pattern=re.compile("test_cases")):
    if pattern.match(line):
        return True
    else:
        return False

def def_setup(line, write,
              pattern=re.compile("(?P<indentation>\s*)"
                                 "def (?P<function_name>setup)"
                                 "(?P<rest>.*)"
                                 )):
    match = pattern.match(line)
    if not match:
        return False
    for test in TESTS:
        write("%sdef _pre%s\n" % (match.group('indentation'),
                                  match.group('rest')))
    return True

def def_shutdown(line, write,
                 pattern=re.compile("(?P<indentation>\s*)"
                                    "def (?P<function_name>shutdown)"
                                    "(?P<rest>.*)"
                                 )):
    match = pattern.match(line)
    if not match:
        return False
    for test in TESTS:
        write("%sdef _post%s\n" % (match.group('indentation'),
                                  match.group('rest')))
    return True

def convert(in_file=sys.stdin, out_file=sys.stdout):
    for line in in_file.readlines():
        for function in (from_sancho,
                         tested_modules,
                         test_val,
                         test_stmt,
                         test_true,
                         test_bool_true,
                         test_false,
                         test_exc,
                         test_cases,
                         test_seq,
                         test_set,
                         def_setup,
                         def_shutdown,
                         class_testscenario,
                         parse_args,
                         coverage_line,
                         run_scenarios):
            if function(line, out_file.write):
                break
        else:
            out_file.write(line)


def convert_main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.set_description("Convert sancho TestScenario file to UTest format.")
    parser.add_option(
        '-i', '--in', dest="in_file", default=None,
        help="TestScenario file to be converted. (default stdin)")
    parser.add_option(
        '-o', '--out', dest="out_file", default=None,
        help="Output file (default stdout)")
    (options, args) = parser.parse_args()
    if options.in_file:
        infile = open(options.in_file, 'r')
    else:
        infile = sys.stdin
    if options.out_file:
        outfile = open(options.out_file, 'w')
    else:
        outfile = sys.stdout
    convert(infile, outfile)

if __name__ == '__main__':
    convert_main()


