# Smug
# Copyright 2008 Andrew McNabb <amcnabb-smug@mcnabbs.org>
#
# This file is part of Smug.
#
# Smug is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Smug is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.


class Config(object):
    """Process configuration queries using a hierarchy of .smug files.
    
    The DotSmug objects are processed in the order in which they are passed
    in.  Thus, the innermost DotSmug should be first in the list.
    """
    def __init__(self, dotsmugs):
        self.dotsmugs = dotsmugs

    def directory_index(self):
        """Find the directory index."""
        for dotsmug in self.dotsmugs:
            index = dotsmug.directory_index
            if index is not None:
                return index
        return None

    def template(self):
        """Find the default template"""
        for dotsmug in self.dotsmugs:
            template = dotsmug.template
            if template is not None:
                return template
        return None

    def default_mimetype(self):
        """Find the default mimetype."""
        for dotsmug in self.dotsmugs:
            mimetype = dotsmug.default_mimetype
            if mimetype is not None:
                return mimetype
        return None

    def convert_sources(self, path):
        """Iterate over convert commands which apply to the given request.

        Yields source_path and using.
        """
        for dotsmug in self.dotsmugs:
            for convert_line in dotsmug.convert:
                convert_to = convert_line['to']
                if path.endswith(convert_to):
                    convert_from = convert_line['from']
                    convert_using = convert_line['using']
                    base = path[0:-len(convert_to)]
                    source_path = base + convert_from

                    # in the future, a SMUG_DEBUG option should make this print happen:
                    #print 'request: %s, source: %s, using: %s' % (path, source_path, convert_using)

                    yield source_path, convert_using


class DotSmugError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return 'Error in .smug: %s' % self.text

class DotSmug(object):
    """Parse a .smug file.
    
    The directory_index directive sets the directory_index attribute:
    >>> teststr = "directory_index abc"
    >>> config = DotSmug(teststr)
    >>> config.directory_index
    'abc'
    >>>

    The directory_index directive may only be specified once:
    >>> teststr = '''directory_index abc
    ... directory_index extra_line'''
    >>> try: config = DotSmug(teststr)
    ... except DotSmugError:
    ...   print 'failed'
    failed
    >>>

    Exactly one argument must be given for directory_index:
    >>> teststr = "directory_index abc extra"
    >>> try: config = DotSmug(teststr)
    ... except DotSmugError:
    ...   print 'failed'
    failed
    >>>

    """

    def __init__(self, dotsmugstr):
        self.tokenizer = line_tokenizer(dotsmugstr)

        self.directory_index = None
        self.default_mimetype = None
        self.template = None
        self.convert = []

        self.parse()

    def parse(self):
        """Parse the .smug file."""

        valid_directives = ('convert', 'directory_index', 'default_mimetype','template')

        for line in self.tokenizer:
            if not line:
                continue
            directive = line[0]
            if directive in valid_directives:
                subparser_name = 'parse_%s' % directive
                subparser = getattr(self, subparser_name)
                subparser(line)
            else:
                raise DotSmugError('unknown directive in .smug file.')

    def parse_convert(self, line):
        """Parse a convert directive."""

        valid_arguments = ('from', 'to', 'using')
        args = dict([(argname, None) for argname in valid_arguments])

        it = iter(line[1:])
        while True:
            try:
                argname = it.next()
            except StopIteration:
                break

            if argname not in args:
                raise DotSmugError('invalid argument name: %s.' % argname)

            if args[argname] is not None:
                raise DotSmugError('argument "%s" specified more than once.'
                        % argname)

            try:
                argvalue = it.next()
            except StopIteration:
                raise DotSmugError('no value for argument "%s".' % argname)

            args[argname] = argvalue

        # default value should be empty string
        for argname in valid_arguments:
            if args[argname] is None:
                args[argname] = ''

        self.convert.append(args)

    def parse_directory_index(self, line):
        """Parse the directory_index directive."""

        if self.directory_index is not None:
            raise DotSmugError('directory_index specified more than once.')
        if len(line) != 2:
            raise DotSmugError('wrong number of arguments to directory_index.')

        self.directory_index = line[1]

    def parse_template(self, line):
        """Parses the template directive."""

        if self.template is not None:
            raise DotSmugError('template specified more than once.')
        if len(line) != 2:
            raise DotSmugError('wrong number of arguments to template.')
        self.template = line[1]

    def parse_default_mimetype(self, line):
        """Parse the default_mimetype directive."""

        if self.default_mimetype is not None:
            raise DotSmugError('default_mimetype specified more than once.')
        if len(line) != 2:
            raise DotSmugError('wrong number of arguments to default_mimetype.')

        self.default_mimetype = line[1]


def line_tokenizer(inputstring):
    r"""Yield a list of tokens for each line in a file.

    If a quoted string is incomplete at the end of a physical line, the
    logical line continues to the next line.  Likewise, join two lines if
    the first line ends in a backslash.

    Setup a test file:
    >>> teststr = r'''First line.
    ... Beginning of second \
    ... line and end.
    ... Beginning of "third
    ... line" and end.'''
    >>>

    Make sure that the lexical analyzer works:
    >>> it = line_tokenizer(teststr)
    >>> it.next()
    ['First', 'line.']
    >>> it.next()
    ['Beginning', 'of', 'second', 'line', 'and', 'end.']
    >>> it.next()
    ['Beginning', 'of', 'third\nline', 'and', 'end.']
    >>>
    """
    from shlex import split

    logical_line = ''
    tokens = []
    for physical_line in inputstring.splitlines(True):
        logical_line += physical_line

        try:
            new_tokens = split(logical_line, comments=True)
        except ValueError:
            # Unmatched quote at end of line: grab another physical line.
            continue

        if new_tokens and new_tokens[-1] == '\n':
            # Continuation (line ends in backslash)
            tokens += new_tokens[:-1]
            # Grab another logical line.
            logical_line = ''
            continue
        else:
            # complete line
            tokens += new_tokens
            yield tokens

        logical_line = ''
        tokens = []

    if logical_line:
        # End of file has been reached but logical_line has not been cleared.
        raise ValueError("Syntax error: unmatched quote at EOF")


def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()

# vim: et sw=4 sts=4
