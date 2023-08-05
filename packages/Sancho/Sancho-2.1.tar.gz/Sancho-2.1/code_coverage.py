"""sancho.code_coverage

Provides code coverage analysis.
"""

import sys, dis, types
from sets import Set

try:
    _findlinestarts = dis.findlinestarts
except AttributeError:
    # Python 2.3 needs this function
    def _findlinestarts(code):
        byte_increments = [ord(c) for c in code.co_lnotab[0::2]]
        line_increments = [ord(c) for c in code.co_lnotab[1::2]]

        lastlineno = None
        lineno = code.co_firstlineno
        addr = 0
        for byte_incr, line_incr in zip(byte_increments, line_increments):
            if byte_incr:
                if lineno != lastlineno:
                    yield (addr, lineno)
                    lastlineno = lineno
                addr += byte_incr
            lineno += line_incr
        if lineno != lastlineno:
            yield (addr, lineno)


def _find_executable_lines(code, executable_lines=None):
    if executable_lines is None:
        executable_lines = Set()
    for addr, lineno in _findlinestarts(code):
        executable_lines.add(lineno)
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            if const.co_filename == code.co_filename:
                _find_executable_lines(const, executable_lines)
    return executable_lines

class CoverageTrace:
    def __init__(self, modules):
        """modules : list of modules for which to show coverage
        """
        self.counts = {}  # {modulename: {lineno: count}}
        self.code_objects = {} # {modulename: {code_object}}
        for modulename in modules:
            self.counts[modulename] = {}
            self.code_objects[modulename] = Set()

    def _trace(self, frame, why, arg):
        if why == 'line':
            modulename = frame.f_globals.get("__name__", "<unnamed module>")
            if modulename in self.counts:
                # record line number of every trace
                lineno = frame.f_lineno
                executed_lines = self.counts[modulename]
                executed_lines[lineno] = executed_lines.get(lineno, 0) + 1
                if frame.f_code not in self.code_objects[modulename]:
                    self.code_objects[modulename].add(frame.f_code)
        return self._trace

    def runfunc(self, func, *args, **kw):
        result = None
        saved_trace = sys._getframe().f_trace
        sys.settrace(self._trace)
        try:
            result = func(*args, **kw)
        finally:
            sys.settrace(saved_trace)
        return result

    def report(self, outfile=sys.stdout, show_lines=1):
        for modulename in self.counts.keys():
            executed_lines = self.counts[modulename]
            outfile.write('%s: ' % modulename)
            if not executed_lines:
                # module as not executed as all
                outfile.write("not executed\n")
                continue
            outfile.write('\n')

            filename = sys.modules[modulename].__file__
            if filename[-4:] == ".pyc" or filename[-4:] == ".pyo":
                filename = filename[:-4] + '.py'
            elif filename[-5:] == ".ptlc":
                filename = filename[:-1]

            try:
                lines = open(filename).readlines()
            except IOError, exc:
                sys.stderr.write("%s: Could not open %r: %s - skipping\n" %
                                 ("trace", filename, exc.strerror))
                continue

            executable_lines = Set()
            for code_object in self.code_objects[modulename]:
                _find_executable_lines(code_object, executable_lines)

            for lineno, line in enumerate(lines):
                lineno += 1
                if lineno in executed_lines:
                    outfile.write('%5d: ' % executed_lines[lineno])
                else:
                    if lineno in executable_lines:
                        outfile.write('@%-5d>' % lineno)
                    else:
                        outfile.write(' '*7)
                outfile.write(line)


def report_coverage(modules, func, *args, **kwargs):
    ct = CoverageTrace(modules)
    rv = ct.runfunc(func, *args, **kwargs)
    ct.report()
    return rv
