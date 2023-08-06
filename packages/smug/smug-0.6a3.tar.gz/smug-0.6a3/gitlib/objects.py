# Gitlib
# Copyright 2008-2009 Andrew McNabb <amcnabb-smug@mcnabbs.org>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Git Object implementations.

Real git objects are immutable, but we need to provide a mutable interface.
As a result, a GitObject starts off as "fresh" (mutable).  Once it is
"frozen", the object name and other properties can be computed, but nothing
can be changed.  To make a change, a new GitObject must be created using the
"copy" method.
"""


import codecs
hex_codec = codecs.lookup('hex_codec')


def frozen_only_property(cache_name):
    """A decorator for defining properties that require freezing.

    Usage is pretty simple.  Just give it the name of the cache variable to
    use.  The name of your function will be the name of the property.

    >>> class SomeGitObject(GitObject):
    ...     _type = 'fake_type'
    ...     hello = None
    ...     @frozen_only_property('_cache_variable')
    ...     def xyz(self):
    ...         return self.hello
    >>> test = SomeGitObject()
    >>> test.hello = 4
    >>> test.xyz
    Traceback (most recent call last):
        ...
    AttributeError: GitObject is not frozen.
    >>> test.freeze()
    >>> test.xyz
    4
    >>>

    Note that after freezing, the value can't be changed:
    >>> test.hello = 5
    >>> test.xyz
    4
    >>>
    """
    def decorator(function):
        """Takes a function which generates the read-only property."""
        def getter(self):
            if not self.frozen:
                raise AttributeError("GitObject is not frozen.")
            try:
                value = getattr(self, cache_name)
            except AttributeError:
                value = None
            if value is None:
                value = function(self)
                setattr(self, cache_name, value)
            return value

        return property(getter, doc=function.__doc__)

    return decorator


def fresh_only_property(cache_name):
    """A property that can only be set before freezing.

    >>> class SomeGitObject(GitObject):
    ...     _type = 'fake_type'
    ...     xyz = fresh_only_property('_cache_variable')
    >>> test = SomeGitObject()
    >>> test.xyz = 4
    >>> test.freeze()
    >>> test.xyz = 5
    Traceback (most recent call last):
        ...
    AttributeError: Attribute can only be set before freezing.
    >>> test.xyz
    4
    >>>
    """
    def getter(self):
        try:
            return getattr(self, cache_name)
        except AttributeError(self):
            setattr(self, cache_name, None)
            return None

    def setter(self, value):
        if self.frozen:
            raise AttributeError('Attribute can only be set before freezing.')
        setattr(self, cache_name, value)

    return property(getter, setter)


class GitObject(object):
    """A Git object, which may be a blob, a tree, a commit, or a tag.

    Once a Git object is frozen, it cannot be changed.  However, it can be
    copied.  Certain attributes, such as `gitobject` and `compressed` are not
    available until the object is frozen.  A Git object can be initialized in
    a frozen form by calling the constructor with the raw contents.  Note that
    the contents and fields are always bytes, not Unicode.

    Inheriting objects should set copy, parse_contents, and make_contents.
    """
    _type = None

    _frozen = False
    frozen = property(lambda self: self._frozen,
            doc="A frozen GitObject cannot be modified")

    def __init__(self, contents=None):
        if not self._type:
            raise TypeError("GitObject cannot be instantiated directly.")

        if contents is not None:
            self.set_contents(contents)
            self.freeze()

    def freeze(self):
        """Freeze the Git object"""
        self._frozen = True

    def __str__(self):
        return self.contents

    def set_contents(self, contents):
        """Set contents of the GitObject, not including headers"""
        if self.frozen:
            raise AttributeError("Can't modify a frozen GitObject")
        else:
            self.parse_contents(contents)

    @frozen_only_property('_contents')
    def contents(self):
        """Contents of the GitObject, not including headers."""
        return self.make_contents()

    @frozen_only_property('_gitobject')
    def gitobject(self):
        """Uncompressed GitObject."""
        size = len(self.contents)
        return '%s %s\0%s' % (self._type, str(size), self.contents)

    @frozen_only_property('_compressed')
    def compressed(self):
        """Compressed GitObject."""
        import zlib
        return zlib.compress(self.gitobject)

    @frozen_only_property('_name')
    def name(self):
        """Object name (SHA1 hash of GitObject)."""
        try:
            import hashlib
            hash_constructor = hashlib.sha1
        except ImportError:
            import sha
            hash_constructor = sha.sha
        hash_obj = hash_constructor(self.gitobject)
        return hash_obj.hexdigest()

    def copy(self, contents):
        """Creates a mutable copy of a Git object.

        This must be implemented by individual GitObject classes.
        """
        raise NotImplementedError

    def make_contents(self):
        """Consolidates individual fields to create the full Git contents.

        This must be implemented by individual GitObject classes.
        """
        raise NotImplementedError

    def parse_contents(self, contents):
        """Parses fields from the contents of a Git object.

        This must be implemented by individual GitObject classes.
        """
        raise NotImplementedError


class Blob(GitObject):
    """A blob object that may be added to a Git repository.

    The text of a blob is bytes (binary files may not be valid UTF-8).
    """

    _type = 'blob'

    _text = ''
    text = fresh_only_property('_text')

    def copy(self):
        blob = Blob()
        blob._text = self._text
        return blob

    def make_contents(self):
        return self._text

    def parse_contents(self, contents):
        self._text = contents


class TreeEnt(object):
    r"""Entry in a Tree.
    
    All attributes are read-only.

    >>> ent = TreeEnt('abc', 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391',
    ...         '100644')
    >>> expected = ('100644 abc\x00' +
    ...     '\xe6\x9d\xe2\x9b\xb2\xd1\xd6CK\x8b)\xaewZ\xd8\xc2\xe4\x8cS\x91')
    >>> str(ent) == expected
    True
    >>>
    """
    filename = property(lambda self: self._filename)
    name = property(lambda self: self._name)
    mode = property(lambda self: self._mode)

    def __init__(self, filename, name, mode):
        self._filename = filename
        self._name = name
        self._mode = mode

    def is_dir(self):
        import stat
        mode = int(self.mode, 8)
        return stat.S_ISDIR(mode)

    def __str__(self):
        raw_name, bytes_consumed = hex_codec.decode(self._name)
        return ''.join((self._mode, ' ', self._filename, '\0', raw_name))


class Tree(GitObject):
    """A tree object that may be added to a Git repository.
    
    >>> t = Tree()
    >>> t.add_file('abc', 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391', 'blob')
    True
    >>> t.add_file('xyz', '484ba93ef5b0aed5b72af8f4e9dc4cfd10ef1a81', 'blob')
    True
    >>> contents = t.make_contents()
    >>>

    >>> u = Tree()
    >>> u.parse_contents(contents)
    >>>
    """
    _type = 'tree'

    def __init__(self, *args):
        self._filemap = {}
        GitObject.__init__(self, *args)

    def make_contents(self):
        return ''.join([str(self._filemap[k]) for k in sorted(self._filemap)])

    def parse_contents(self, contents):
        import sys
        while contents:
            # Mode.
            space = contents.index(' ')
            mode = contents[:space]

            # Filename.
            null = contents.index('\0', space + 1)
            filename = contents[space + 1: null]

            # Object Name (SHA-1).
            name_length = 20
            start_of_name = null + 1
            end_of_name = start_of_name + name_length
            raw_name = contents[start_of_name: end_of_name]
            name, bytes_consumed = hex_codec.encode(raw_name)

            # Create the Tree Entry.
            entry = TreeEnt(filename, name, mode)
            self._filemap[filename] = entry

            contents = contents[end_of_name:]

    def add_file(self, filename, name, type, mode=None, replace=False):
        """Adds an object to the tree.

        The filename, name (SHA-1), and type must be specified.  The mode
        defaults to '100644' for blobs and '040000' for trees.  If replace
        is given and True, then any existing file with the same filename
        will be replaced.

        Returns True if the operation succeeded, and False otherwise (i.e.,
        filename already exists).  An exception is raised if the Tree is
        frozen.
        """
        assert not self.frozen

        if (not replace) and (filename in self._filemap):
            return False
        if '/' in filename:
            raise ValueError('Filenames may not contain slashes.')

        if mode is None:
            if type == 'blob':
                mode = '100644'
            elif type == 'tree':
                mode = '040000'

        self._filemap[filename] = TreeEnt(filename, name, mode)
        return True

    def entries(self, reverse=False):
        """Iterates over the tree entries in sorted order.
        
        Yields (path, entry) pairs.
        """
        return sorted(self._filemap.iteritems(), reverse=reverse)


class Commit(GitObject):
    r"""A commit object that may be added to a Git repository.

    >>> tree = '7c6cf9b169ab51858fbbb77f352d0de249bb1e97'
    >>> parent = 'ecf5e79f6dc40b9f517baf6de5755e31ed4188fb'
    >>> author = 'Andrew McNabb <amcnabb@mcnabbs.org> 1219616814 -0600'
    >>> committer = author
    >>> message = 'added mdadm.conf\n'
    >>> contents = ('tree %s\nparent %s\nauthor %s\ncommitter %s\n\n%s' %
    ...     (tree, parent, author, committer, message))
    >>> commit = Commit(contents)
    >>> commit.freeze()
    >>> commit.contents == contents
    True
    >>>
    """

    _type = 'commit'

    _tree = ''
    tree = fresh_only_property('_tree')
    _parents = ()
    parents = fresh_only_property('_parents')
    _author = ''
    author = fresh_only_property('_author')
    _committer = ''
    committer = fresh_only_property('_committer')
    _message = ''
    message = fresh_only_property('_message')

    def copy(self):
        commit = Commit()
        commit.tree = self.tree
        commit.parents = list(self.parents)
        commit.author = self.author
        commit.committer = self.committer
        commit.message = self.message
        return commit

    def make_contents(self):
        lst = []
        lst.append('tree %s' % self.tree)
        for parent in self.parents:
            lst.append('parent %s' % parent)
        lst.append('author %s' % self.author)
        lst.append('committer %s' % self.committer)
        lst.append('')
        lst.append(self.message)
        return '\n'.join(lst)

    def parse_contents(self, contents):
        """Sets the individual fields of a commit based on its contents."""
        header, message = contents.split('\n\n', 1)
        for line in header.splitlines():
            key, value = line.split(None, 1)
            if key in ('tree', 'author', 'committer'):
                setattr(self, key, value)
            elif key == 'parent':
                self.parents = self.parents + (value,)
            else:
                print 'Warning: unknown key "%s"' % key
        self.message = message

        # Sanity check:
        #assert self.make_contents() == contents
        """
        if self.make_contents() != contents:
            print "Error! Contents doesn't match str(self)!"
            print str(self)
            print contents
            raise RuntimeError
        """


# vim: et sw=4 sts=4
