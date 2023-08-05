import string
from types import *

class IndentedFile:
    """File-like object that adds indentation to each output line.
    Supports all file methods except 'read()', 'readline()',
    'readlines()', and 'readinto()'."""

    def __init__ (self, file, indent=2, base_indent=None):
        """Initialize a new IndentedFile.  'file' must be a file or
        file-like object opened for writing; 'indent', if given, is the
        string to prepend to each line *or* the number of spaces to
        prepend."""

        self.file = file
        if type (indent) is IntType:
            self.indent = ' ' * indent
        elif type (indent) is StringType:
            self.indent = indent
        else:
            raise TypeError, "'indent' must be a string or an integer"

        if base_indent is None:
            self.base_indent = indent
        else:
            self.base_indent = base_indent
        self.at_start = 1               # at start of a line?

        for method_name in ('close', 'tell', 'seek', 'isatty',
                            'flush', 'truncate', 'fileno'):

            # Don't get uptight if we can't find a method on the
            # supposed file-like object -- it might be a user-defined
            # file-like object, or this might be JPython, where even
            # standard file objects don't provide 'isatty()' or
            # 'truncate()'.
            try:
                setattr (self, method_name,
                         getattr (self.file, method_name))
            except AttributeError:
                pass


    def write (self, str):
        lines = string.split (str, '\n')

        if len (lines) == 1:            # no newlines
            if self.at_start:
                self.file.write (self.indent)
            self.file.write (lines[0])
            self.at_start = 0           # next 'write' continues this line

        else:

            # write the first line (which might be a continuation of
            # a previous line)
            if self.at_start:
                self.file.write (self.indent)
            self.file.write (lines[0] + '\n')

            # now write all the complete lines in 'str', ie. everything
            # up to the final newline
            for l in lines[1:-1]:
                self.file.write (self.indent + l + '\n')
            self.at_start = 1

            # and write any text that follows the final newline
            if lines[-1]:
                self.file.write (self.indent + lines[-1])
                self.at_start = 0


    def writelines (self, lines):
        for l in lines:
            self.write (l)


    def indent_more (self, indent=None):

        if indent is None:
            self.indent_more (self.base_indent)
            return

        if type (indent) is IntType:
            self.indent = self.indent + (' ' * indent)
        elif type (indent) is StringType:
            self.indent = self.indent + indent
        else:
            raise TypeError, "'indent' must be a string or an integer"

    def indent_less (self, indent=None):

        if indent is None:
            self.indent_less (self.base_indent)
            return

        if type (indent) is IntType:
            self.indent = self.indent[0:-indent]
        elif type (indent) is StringType:
            if self.indent[-len(indent):] == indent:
                self.indent = self.indent[0:-len(indent)]
            else:
                raise ValueError, \
                      "indentation string '%s' does not end in '%s'" % \
                      (self.indent, indent)
        else:
            raise TypeError, "'indent' must be a string or an integer"


if __name__ == "__main__":
    import os

    f = open ("foo", "w")
    indf = IndentedFile (f)
    indf.write ("Line 1\n")
    indf.write ("Line 2\nLine 3")
    indf.write ("...continued\n")
    indf.indent_more()
    indf.writelines (["Line 4\n", "Line 5", "...continued\n", "Line 6"])
    indf.indent_less()
    indf.write ("\n")
    indf.write ("Line 7") ; indf.write ("\n")
    indf.indent_less()
    indf.write ("Line 8\nLine 9\n")
    indf.close()

    expect = ["  Line 1",
              "  Line 2",
              "  Line 3...continued",
              "    Line 4",
              "    Line 5...continued",
              "    Line 6",
              "  Line 7",
              "Line 8",
              "Line 9",
             ]

    print "Expected output:"
    for line in expect:
        print line

    print "Actual output:"
    os.system ("cat foo")
    
