"""sancho.code_coverage

Provides code coverage analysis for testing
"""

# created 2000/07/06, Neil Schemenauer based on trace.py

__revision__ = "$Id: code_coverage.py 22221 2003-08-21 15:46:53Z nascheme $"

# Example Usage:
#
# import code_coverage
# co = code_coverage.Coverage()
# co.run('main()')
# co.write_results()
#
# or
#
# $ python code_coverage.py "import mymodule; mymodule.main()"

# trace.py
# Copyright 2000, Mojam Media, Inc., all rights reserved.
# Author: Skip Montanaro
#
# Copyright 1999, Bioreason, Inc., all rights reserved.
# Author: Andrew Dalke
#
# Copyright 1995-1997, Automatrix, Inc., all rights reserved.
# Author: Skip Montanaro
#
# Copyright 1991-1995, Stichting Mathematisch Centrum, all rights reserved.
#
#
# Permission to use, copy, modify, and distribute this Python software and
# its associated documentation for any purpose without fee is hereby
# granted, provided that the above copyright notice appears in all copies,
# and that both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of neither Automatrix,
# Bioreason or Mojam Media be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior permission.

import sys, os, string, types, tokenize, token


def _find_lines_from_code(code, strs):
    """Return dict where keys are lines in the line number table."""
    linenos = {}
    line_increments = [ord(c) for c in code.co_lnotab[1::2]]
    lineno = code.co_firstlineno
    for li in line_increments:
        lineno += li
        if lineno not in strs:
            linenos[lineno] = 1
    return linenos


def _find_lines(code, strs):
    """Return lineno dict for all code objects reachable from code."""
    # get all of the lineno information from the code of this scope level
    linenos = _find_lines_from_code(code, strs)

    # and check the constants for references to other code objects
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            # find another code object, so recurse into it
            linenos.update(_find_lines(c, strs))
    return linenos


def _find_strings(filename):
    """Return a dict of possible docstring positions.

    The dict maps line numbers to strings.  There is an entry for
    line that contains only a string or a part of a triple-quoted
    string.
    """
    d = {}
    # If the first token is a string, then it's the module docstring.
    # Add this special case so that the test in the loop passes.
    prev_ttype = token.INDENT
    f = open(filename)
    for ttype, tstr, start, end, line in tokenize.generate_tokens(f.readline):
        if ttype == token.STRING:
            if prev_ttype == token.INDENT:
                sline, scol = start
                eline, ecol = end
                for i in range(sline, eline + 1):
                    d[i] = 1
        prev_ttype = ttype
    f.close()
    return d


def find_executable_linenos(filename):
    """Return dict where keys are line numbers in the line number table."""
    try:
        prog = open(filename).read()
    except IOError, err:
        print >> sys.stderr, ("Not printing coverage data for %r: %s"
                              % (filename, err))
        return {}
    code = compile(prog, filename, "exec")
    strs = _find_strings(filename)
    return _find_lines(code, strs)


class Ignore:
    def __init__(self, modules = None, dirs = None):
        self._mods = modules or []
        self._dirs = dirs or []

        self._ignore = { '<string>': 1 }


    def names(self, filename, modulename):
        if self._ignore.has_key(modulename):
            return self._ignore[modulename]

        # haven't seen this one before, so see if the module name is
        # on the ignore list.  Need to take some care since ignoring
        # "cmp" musn't mean ignoring "cmpcache" but ignoring
        # "Spam" must also mean ignoring "Spam.Eggs".
        for mod in self._mods:
            if mod == modulename:  # Identical names, so ignore
                self._ignore[modulename] = 1
                return 1
            # check if the module is a proper submodule of something on
            # the ignore list
            n = len(mod)
            # (will not overflow since if the first n characters are the
            # same and the name has not already occured, then the size
            # of "name" is greater than that of "mod")
            if mod == modulename[:n] and modulename[n] == '.':
                self._ignore[modulename] = 1
                return 1

        # Now check that __file__ isn't in one of the directories
        if filename is None:
            # must be a built-in, so we must ignore
            self._ignore[modulename] = 1
            return 1

        # Ignore a file when it contains one of the ignorable paths
        for d in self._dirs:
            # The '+ os.sep' is to ensure that d is a parent directory,
            # as compared to cases like:
            #  d = "/usr/local"
            #  filename = "/usr/local.py"
            # or
            #  d = "/usr/local.py"
            #  filename = "/usr/local.py"
            if string.find(filename, d + os.sep) == 0:
                self._ignore[modulename] = 1
                return 1

        # Tried the different ways, so we don't ignore this module
        self._ignore[modulename] = 0
        return 0

class Coverage:
    def __init__(self, modules=None):
        """modules : list of modules for which to show coverage
        default is all modules"""
        self.modules = {} # module -> filename
        self.counts = {}  # (modulename, linenumber) -> count
        if modules is None:
            self.show_all = 1
        else:
            self.show_all = 0
            for module in modules:
                self.modules[module] = None

    def trace(self, frame, why, arg):
        if why == 'line':
            modulename = frame.f_globals.get("__name__", "<unnamed module>")
            if self.show_all or self.modules.has_key(modulename):
                # something is fishy about getting the file name
                filename = frame.f_globals.get("__file__", None)
                if filename is None:
                    filename = frame.f_code.co_filename
                self.modules[modulename] = filename

                lineno = frame.f_lineno

                # record the file name and line number of every trace
                key = (modulename, lineno)
                self.counts[key] = self.counts.get(key, 0) + 1

        return self.trace

    def run(self, cmd):
        import __main__
        dict = __main__.__dict__
        sys.settrace(self.trace)
        try:
            exec cmd in dict, dict
        finally:
            sys.settrace(None)

    def runctx(self, cmd):
        import __main__
        dict = __main__.__dict__
        sys.settrace(self.trace)
        try:
            exec cmd in dict, dict
        finally:
            sys.settrace(None)

    def runfunc(self, func, *args, **kw):
        result = None
        sys.settrace(self.trace)
        try:
            result = apply(func, args, kw)
        finally:
            sys.settrace(None)
        return result

    def write_results(self, outfile=sys.stdout, show_lines=1):
        import re
        # turn the counts data ("(module, lineno) = count") into something
        # accessible on a per-module basis
        per_module = {}
        for modulename, lineno in self.counts.keys():
            try:
                lines_hit = per_module[modulename]
            except KeyError:
                lines_hit = per_module[modulename] = {}
            lines_hit[lineno] = self.counts[(modulename, lineno)]

        # there are many places where this is insufficient, like a blank
        # line embedded in a multiline string.
        blank = re.compile(r'^\s*(#.*)?$')

        for modulename, filename in self.modules.items():
            if filename == '<string>':
                continue
            outfile.write('%s: ' % modulename)
            if filename is None:
                # module as not executed as all
                outfile.write("not executed\n")
                continue
            if filename[-4:] == ".pyc" or filename[-4:] == ".pyo":
                orig_filename = filename[:-4] + '.py'
            else:
                orig_filename = filename

            if show_lines:
                outfile.write('\n')

            # Get the original lines from the .py file
            try:
                lines = open(orig_filename, 'r').readlines()
            except IOError, err:
                sys.stderr.write(
                    "%s: Could not open %s for reading because: %s - skipping\n" % \
                    ("trace", `filename`, err.strerror))
                continue

            # get a list of the line numbers which represent executable
            # content (returned as a dict for better lookup speed)
            executable_linenos = find_executable_linenos(orig_filename)

            lines_hit = per_module[modulename]
            num_lines = 0
            num_lines_hit = 0
            for i in range(len(lines)):
                line = lines[i]

                # do the blank/comment match to try to mark more lines
                # (help the reader find stuff that hasn't been covered)
                if lines_hit.has_key(i+1):
                    num_lines_hit = num_lines_hit + 1
                    num_lines = num_lines + 1
                    if show_lines:
                        # count precedes the lines that we captured
                        outfile.write('%5d: ' % lines_hit[i+1])
                elif blank.match(line):
                    # blank lines and comments are preceded by dots
                    if show_lines:
                        outfile.write('    . ')
                else:
                    # lines preceded by no marks weren't hit
                    # Highlight them if so indicated, unless the line contains
                    # '#pragma: NO COVER' (it is possible to embed this into
                    # the text as a non-comment; no easy fix)
                    if executable_linenos.has_key(i+1) and \
                       string.find(lines[i], '#pragma NO COVER') == -1:
                        num_lines = num_lines + 1
                        if show_lines:
                            outfile.write('>>>>>> ')
                    else:
                        if show_lines:
                            outfile.write(' '*7)
                if show_lines:
                    outfile.write(string.expandtabs(lines[i], 8))
            if num_lines == 0:
                num_lines = 1 # avoid blowup on empty files
            outfile.write("%3.1f%% (%d/%d)\n" %
                    ((100.0*num_lines_hit)/num_lines, num_lines_hit, num_lines))



def main(stmt):
    co = Coverage()
    co.runctx(stmt)
    co.write_results()
    

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print "Usage: code_coverage.py <statement>"
        sys.exit(1)
