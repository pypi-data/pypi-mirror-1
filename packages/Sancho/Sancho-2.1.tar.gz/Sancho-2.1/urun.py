#!/www/python/bin/python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/sancho/urun.py $
$Id: urun.py 26920 2005-06-16 17:26:14Z rmasse $

Command line tool for running utest_*py scripts.
"""

import os
from optparse import OptionParser
from sancho import code_coverage

def run_utests(filenames):
    for filename in filenames:
        execfile(filename, {'__name__': '__main__', '__file__': filename})

def main():
    usage = 'usage: %prog [-c <modulename>] [filename | directory]'
    parser = OptionParser(usage=usage)
    parser.set_description('Run a set of utest modules.  Each file named '
                           'will be executed.  If a directory name is '
                           'provided then all files under that directory '
                           'that match the pattern utest_*.py will executed.')
    parser.add_option('-c', '--show-coverage',
                      dest='module', default=[], action='append',
                      help='After running tests, show code coverage of the '
                           'named module (provide the name, not the '
                           'filename).')
    (options, args) = parser.parse_args()
    matches = []
    args = args or ['.']
    for pat in args:
        if os.path.isdir(pat):
            for dirpath, dirnames, filenames in os.walk(pat):
                for name in filenames:
                    if name.startswith('utest_') and name.endswith('.py'):
                        matches.append(os.path.join(dirpath, name))
        else:
            matches.append(pat)
    matches.sort()
    if options.module:
        code_coverage.report_coverage(options.module, run_utests, matches)
    else:
        run_utests(matches)


if __name__ == '__main__':
    main()
