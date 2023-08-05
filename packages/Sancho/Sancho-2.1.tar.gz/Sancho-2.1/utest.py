"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/sancho/utest.py $
$Id: utest.py 26714 2005-04-28 19:59:19Z dbinger $

a lean unit test framework
"""

import sys, cStringIO, traceback, inspect

class UTest:

    def __init__(self):
        """
        Run each method of self whose name does not start with an underscore
        as a test.
        Run self._pre() before each test method.
        Run self._post() after each test method.
        Trap all output to stdout, except when an exception is raised
        in the method being called.
        If an exception is raised in a method call, print any generated
        output and a traceback, and proceed to the next method call.
        """

        def run(method, name):
            """(method:MethodType, name:str)
            Run method, label output using name.
            The method runs with stdout redirected to a cStringIO.
            If it runs without raising an exception, no output is generated.
            If an exception is generated, it prints the accumulated output
            and a traceback.
            """
            old_stdout = sys.stdout
            sys.stdout = cStringIO.StringIO()
            try:
                print '.-- %s' % name
                try:
                    method(self)
                except KeyboardInterrupt:
                    raise
                except:
                    # print traceback, restore stdout
                    data = ''.join(traceback.format_exception(*sys.exc_info()))
                    for line in data.rstrip().split('\n'):
                        sys.stdout.write('|' + line + '\n')
                    sys.__stdout__.write(sys.stdout.getvalue())
            finally:
                sys.stdout = old_stdout
        names = [name for name in dir(self.__class__)
                 if not name.startswith('_')]
        names.sort()
        printed = False
        for name in names:
            check = getattr(self.__class__, name)
            if inspect.ismethod(check):
                if not printed:
                    print ("%s: %s:" % (inspect.getsourcefile(check),
                                        self.__class__.__name__))
                    printed = True
                run(self.__class__._pre, '%s: _pre' % name)
                run(check, name)
                run(self.__class__._post, '%s: _post' % name)

    def _pre(self):
        """
        Executed before each test method.
        Override as needed.
        """

    def _post(self):
        """
        Executed after each test method.  Override as needed.
        This default removes any attributes whose names do not start with '_'
        """
        for name in self.__dict__.keys():
            if not name.startswith('_'):
                delattr(self, name)


def raises(exc, func, *args, **kwargs):
    """(exception, func, *args, **kwargs) -> bool

    Return True if func(*args, **kwargs) raises exc.
    """
    try:
       func(*args, **kwargs)
    except exc:
        return True
    else:
        return False

