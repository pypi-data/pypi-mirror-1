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

"""Git Index (for modifying and merging trees)."""


import os
from objects import Blob


# TODO: Note that we could create a Tree object and write it with git-mktree
# instead of having to create an entire Index.  I would expect this to reduce
# overhead for any case without merging.
class Index(object):
    """Git index or directory cache

    All commits and merges are staged in an index file.  The Index class
    manages such a file.  Specify the commit to read from as a SHA-1.
    """

    def __init__(self, repository, commit, indexfile=None):
        self.repository = repository
        self.commit = commit
        if indexfile is None:
            from tempfile import mkstemp
            fd, indexfile = mkstemp(prefix='python-gitlib-index')
            os.close(fd)
            self.tempfile = True
        else:
            self.tempfile = False
        self.indexfile = indexfile

        if commit:
            self.git_command('read-tree', commit)
        else:
            self.git_command('read-tree')

    def __del__(self):
        if self.tempfile:
            os.unlink(self.indexfile)

    def git_command(self, *args, **kwds):
        """Call repository.git_command(), with the index file in the env.
        """
        if 'env' in kwds:
            kwds = kwds.copy()
            kwds['env'] = kwds['env'].copy()
        else:
            kwds['env'] = {}
        kwds['env']['GIT_INDEX_FILE'] = self.indexfile
        return self.repository.git_command(*args, **kwds)

    def add(self, path, name, mode='100644', replace=False):
        """Add a file directly to the index.

        The git object with SHA-1 name should already be added to the
        repository.  By default, it will fail if the file path already exists
        in the index; specify replace to override.

        More information on mode (?)
        It looks like 100644 is a very common mode.
        """
        args = ['update-index', '--add']
        if replace:
            args.append('--replace')
        args += ['--cacheinfo', mode, name, path]
        kwds = {'ignore_output': True}
        self.git_command(*args, **kwds)

    def remove(self, path):
        """Remove a file from the index."""
        self.git_command('update-index', '--force-remove', path,
                ignore_output=True)

    def write(self):
        """Create and write a new tree object (from the index).

        Returns the SHA-1 object name of the new tree object.
        """
        output = self.git_command('write-tree')
        return output.rstrip()

    def merge(self, mergebase, other_commit, resolutions=None):
        """Perform a 3-way merge into the index.

        A 3-way merge leaves base_commit entries in stage1, self_commit
        entries in stage2, and other_commit entries in stage3.  If possible,
        entries are "collapsed" back to stage0 (the merged tree).  Anything
        that's not automatically collapsed to stage0 needs to be dealt with
        individually.  Any file with any difference will be left with three
        separate entries in the index. Read the man page for git-read-tree for
        more info.

        You can specify resolutions: a dictionary that maps paths to (name,
        mode) pairs.  For any entry in the resolutions dict, we will add the
        name, mode to the index for that path, thus resolving the conflict
        at that path.

        After all of this, we will return a list of unresolved Conflicts.
        """
        if resolutions is None:
            resolutions = {}

        self.git_command('read-tree', '-m', '--aggressive', '-i', mergebase,
                self.commit, other_commit, ignore_output=True)

        for path in resolutions:
            name, mode = resolutions[path]
            self.add(path, name, mode, replace=True)

        output = self.git_command('merge-index', 'echo', '-a')
        lines = output.splitlines()
        conflicts = [Conflict(line, self) for line in lines if line.strip()]
        unresolved = []
        # TODO: Try to resolve some easy stuff here.  Note that
        # git-merge-one-file is problematic since it tries to do things in the
        # working tree, but it still has some useful info about performing
        # merges.  Some stuff is already taken care of by --aggressive, but at
        # least some of the stuff in git-merge-one-file would be useful to
        # look at.  We should even try to do git-merge-file for the cases
        # where it can solve problems without returning an error code.
        # Anyway, try to fix anything possible, and then return a pruned
        # conflicts list.
        for conflict in conflicts:
            # TODO: Check for mode conflicts.
            contents, conflict_occurred = conflict.merge_file_verbose()
            if conflict_occurred:
                unresolved.append(conflict)
            else:
                blob = Blob(contents)
                self.repository.write(blob)
                # TODO: don't be so lazy about the mode.
                self.add(conflict.path, blob.name, conflict.base_mode)
        return unresolved


class Conflict(object):
    """A conflict from a merge.
    
    Very bad things will happen if you try to change this after creation
    (since we cache the results of merge_file).
    """
    def __init__(self, conflict_str, index):
        self.index = index
        self.repository = index.repository
        (self.base_id, self.current_id, self.other_id,
                self.path, self.base_mode, self.current_mode,
                self.other_mode) = conflict_str.split()
        self._merge_file_cache = None

    def merge_file(self):
        """Try to do a 3-way merge on the files in the conflict.

        Return a string containing the file contents (possibly with conflict
        markers).
        """
        contents, conflicts_occurred = self.merge_file_verbose()
        return contents

    def merge_file_verbose(self):
        """Try to do a 3-way merge on the files in the conflict.

        Return a (str, bool) tuple.  The string contains the file contents
        (possibly with conflict markers), and the bool indicates if there were
        conflicts.
        """
        if self._merge_file_cache is not None:
            return self._merge_file_cache

        unpack_file = self.repository.unpack_file
        current_file = unpack_file(self.current_id)
        base_file = unpack_file(self.base_id)
        other_file = unpack_file(self.other_id)

        try:
            output = self.repository.git_command('merge-file', '-p', '-q',
                    '-L', 'into_branch', '-L', 'merge_base',
                    '-L', 'from_branch', current_file, base_file, other_file)
            conflicts_occurred = False
        except GitProcError, e:
            if e.retcode == 1:
                output = e.gitproc.stdout
            else:
                raise e
            conflicts_occurred = True

        contents = output.read()

        for filename in (current_file, base_file, other_file):
            os.unlink(os.path.join(self.repository.path, filename))

        return_value = (contents, conflicts_occurred)
        self._merge_file_cache = return_value
        return return_value


# vim: et sw=4 sts=4
