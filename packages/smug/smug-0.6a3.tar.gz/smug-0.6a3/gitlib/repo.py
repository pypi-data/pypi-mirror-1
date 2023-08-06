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

"""Git Repository."""


# TODO:
# - Environment variables for git-commit-tree: GIT_AUTHOR_NAME, etc. (?)
# - Better merging

import os, subprocess
from objects import Blob, Commit, Tree
from index import Index


class GitError(RuntimeError):
    pass


class GitProcError(GitError):
    def __init__(self, msg, gitproc, retcode):
        self.msg = msg
        self.gitproc = gitproc
        self.retcode = retcode

    def __str__(self):
        return self.msg


class GitProc(object):
    def __init__(self, *args, **kwds):
        """Popen variant that executes git with args.

        All of the standard Popen keyword args work.  In particular,
        stdin, stdout, env, and cwd are useful.
        """

        self.args = ['git']
        for arg in args:
            if isinstance(arg, unicode):
                self.args.append(arg.encode('utf-8'))
            else:
                self.args.append(arg)
        if 'env' in kwds:
            env = {}
            for key, value in kwds['env'].iteritems():
                if isinstance(value, unicode):
                    value = value.encode('utf-8')
                env[key] = value
            kwds['env'] = env
        self.gitproc = subprocess.Popen(self.args, **kwds)

    stdin = property(lambda self: self.gitproc.stdin)
    stdout = property(lambda self: self.gitproc.stdout)

    def wait(self):
        """Wait for the process to complete
        
        Return the process' return code.
        """
        self.retcode = self.gitproc.wait()
        return self.retcode

    def read(self, input=None):
        """Read from (and write to) the process and wait for it to complete.

        Returns stdout as a string (so this should not be used to read
        large amounts of data).  Also note that this ignores stderr.
        """
        if isinstance(input, unicode):
            input = input.encode('utf-8')
        stdout, stderr = self.gitproc.communicate(input)
        self.retcode = self.gitproc.returncode
        if self.retcode == 0:
            return stdout
        else:
            command = ' '.join(self.args)
            raise GitProcError('Git command failed: "%s"' % command,
                    self.gitproc, self.retcode)


class Repository(object):
    """Interact with a Git repository.

    The repository may be bare or it may have a working directory.
    """
    def __init__(self, path, create=False):
        self.path = path
        self.shared_repository=None

    def git_exec(self, *args, **kwds):
        """Execute git with args and return a GitProc object.

        Changes working directory to the repository before executing.
        Popen arguments can be specified, such as stdin, stdout, and env.
        """
        kwds['cwd'] = self.path
        gitproc = GitProc(*args, **kwds)
        return gitproc

    def git_command(self, *args, **kwds):
        """Execute git with args and wait for completion.
        
        Save standard output (and return a string on completion) unless
        ignore_output=True is specified.  The environment can be specified
        with the env argument (as a dictionary).
        """
        try:
            ignore_output = kwds['ignore_output']
            del kwds['ignore_output']
        except KeyError:
            ignore_output = False

        if ignore_output:
            kwds['stdout'] = open('/dev/null', 'w')
        else:
            kwds['stdout'] = subprocess.PIPE

        gitproc = self.git_exec(*args, **kwds)
        if ignore_output:
            gitproc.wait()
        else:
            return gitproc.read()

    def create(self):
        """Initializes the Git repository.
        
        Raises a GitError if repository initialization fails.
        """
        try:
            os.makedirs(self.path)
        except OSError, e:
            import errno
            if e.errno != errno.EEXIST:
                raise
        self.git_command('--bare', 'init', ignore_output=True)


    def chmod(self, path):
        """Set the permissions of a path to conform to sharedRepository.
        
        This attempts to mimic the actions of Git's adjust_shared_perm
        function in path.c.
        """
        shared = self.shared_repository
        if shared is None:
            # Find whether it's a shared repository
            try:
                output = self.git_command('config', 'core.sharedRepository')
                shared = output.rstrip()
            except GitError:
                shared = ''
            if shared in ('', 'umask'):
                shared = False
            elif shared in ('1', 'group'):
                shared = 'group'
            elif shared in ('2', 'all', 'world', 'everybody'):
                shared = 'everybody'
            else:
                raise GitError('Unknown value of core.sharedRepository: "%s"'
                        % shared)
            self.shared_repository = shared

        if not shared:
            return

        import stat
        st = os.stat(path)
        mode = st.st_mode

        if (mode & stat.S_IRUSR):
            if (shared == 'group'):
                mode |= stat.S_IRGRP
            elif shared == 'everybody':
                mode |= (stat.S_IRGRP|stat.S_IROTH)

        if (mode & stat.S_IWUSR):
            mode |= stat.S_IWGRP

        if (mode & stat.S_IXUSR):
            if (shared == 'group'):
                mode |= stat.S_IXGRP
            elif shared == 'everybody':
                mode |= (stat.S_IXGRP|stat.S_IXOTH)

        if (stat.S_ISDIR(mode)):
                mode |= stat.S_ISGID

        os.chmod(path, mode)

    # TODO: For writing Tree objects, this should call git-mktree instead of
    # trying to write directly to a file.
    def write(self, gitobj):
        """Write a GitObject (Blob, Tree, Commit or Tag) to the repository.
        """
        dirname = gitobj.name[:2]
        filename = gitobj.name[2:]
        dirpath = os.path.join(self.path, 'objects', dirname)
        filepath = os.path.join(dirpath, filename)

        # If the file already exists, there's nothing to do, since objects
        # with the same object name are identical.
        if not os.path.exists(filepath):
            try:
                os.mkdir(dirpath)
                self.chmod(dirpath)
            except OSError, e:
                import errno
                if e.errno != errno.EEXIST:
                    raise
            f = open(filepath, 'w')
            self.chmod(filepath)
            f.write(gitobj.compressed)
            f.close()

    def find_head(self, branch='master'):
        """Find the tree object for the head of a given branch.

        Return the object name (SHA-1) of the tree object.
        Technically we're returning the id of the commit object, but it
        appears that you can use it anywhere you can use a tree object id.
        """
        try:
            output = self.git_command('show-ref', '--heads', branch)
            return output.split()[0]
        except GitProcError:
            return None

    def save_head(self, commit, oldhead, branch='master'):
        """Save a commit object as to the head ref for the given branch.

        Fail if the value of head that we are replacing is not oldhead.
        Otherwise we would have a nasty race condition.  Set oldhead to
        None if you are creating a new branch.
        """
        branchref = os.path.join('refs/heads', branch)
        if oldhead is None:
            oldhead = ''
        proc = self.git_exec('update-ref', branchref, commit, oldhead,
                stdout=open('/dev/null', 'w'))
        retcode = proc.wait()
        return not retcode

    def getname(self, path, branch=None, treename=None):
        """Lookup the object name (SHA-1) of a path within the specified tree.
        
        The tree can be specified with treename (the object name of a commit
        or tree) or with a branch, in which case the head of the branch will
        be used.  It is illegal to specify both.  The path may have a trailing
        slash, in which case the path must refer to a tree.  However, leading
        slashes are invalid (except in the trivial case of the tree "/", which
        it's really a trailing slash).

        Returns the name of the object at the given path, or None if it cannot
        be found.
        """
        if treename is None:
            branch = 'master'
            treename = self.find_head(branch)
            if treename is None:
                #print "Can't find head for branch=%s" % branch
                return None
        elif branch is not None:
            raise ValueError("Branch and treename cannot both be given to " 
                    "getname()")

        # Mimics the behavior of other tools (e.g., `ls /etc/passwd/` fails)
        if path and path[-1] == '/':
            require_tree = True
            path = path[:-1]
        else:
            require_tree = False

        if not path:
            # Special case: `git ls-tree ""` does not show the name of the
            # root tree.
            commit = self.getcommit(treename)
            name = commit.tree
        else:
            if path[0] == '/':
                raise GitError("getname() was given a path with a leading /.")

            ls = self.git_command('ls-tree', treename, path)
            name = None
            if ls:
                fields = ls.split()
                objtype = fields[1]
                if not require_tree or objtype == 'tree':
                    name = fields[2]

        return name

    def gettype(self, name):
        """Get the type of the object identified by the given object name.
        
        For convenience, None is returned if name is not specified.
        """
        if name:
            output = self.git_command('cat-file', '-t', name)
            return output.split()[0]

    def getblob(self, name):
        """Retrieves the blob with the given object name as a Blob object.
        
        For convenience, None is returned if name is not specified.
        """
        if name:
            contents = self.git_command('cat-file', 'blob', name)
            return Blob(contents)

    def getcommit(self, name):
        """Retrieves the blob with the given object name as a Blob object."""
        contents = self.git_command('cat-file', 'commit', name)
        return Commit(contents)

    def gettree(self, name):
        """Retrieves the tree with the given object name as a Tree object."""
        contents = self.git_command('cat-file', 'tree', name)
        return Tree(contents)

    def walktree(self, name, reverse=False):
        """Recursively walks through the tree with the given object name.
        
        Yields (path, object_name) pairs which are sorted within each subtree.
        If reverse is True, entries are sorted in reverse order.
        """
        tree = self.gettree(name)
        for path, entry in tree.entries(reverse):
            if entry.is_dir():
                for subpath, name in self.walktree(entry.name, reverse):
                    yield '/'.join((path, subpath)), name
            else:
                yield path, entry.name

    def unpack_file(self, name):
        """Open the blob with SHA-1 name, and save it to a temporary file.

        Return the filename of the temporary file, which the caller is
        responsible for deleting.
        """
        output = self.git_command('unpack-file', name)
        return output.rstrip()

    def readtree(self, tree):
        """Read a tree into an Index."""
        return Index(self, tree)

    # TODO: Just write a Commit object and call git-update-ref instead of
    # calling the commit function.
    def commit(self, tree, parent_ids, changelog, author_name=None,
            author_email=None):
        """Create a new commit object for the given tree.

        Specify the changelog as a string and the parent commits as list
        of ids of tree objects.  The author name and email may optionally
        be specified.  Return the id of the new commit.
        """
        env = {}
        if author_name:
            env['GIT_AUTHOR_NAME'] = author_name
        if author_email:
            env['GIT_AUTHOR_EMAIL'] = author_email

        args = ['commit-tree', tree]
        for name in parent_ids:
            args += ['-p', name]
        kwds = {'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE,
                'env': env}
        gitproc = self.git_exec(*args, **kwds)
        output = gitproc.read(changelog)

        return output.rstrip()

    def commit_add(self, path, text, parent, changelog, author_name=None,
            author_email=None):
        """Add or change a single file in the tree and commit.
        
        Return the object name (SHA-1) of the new git object.
        """
        if parent:
            index = self.readtree(parent)
        else:
            index = Index(self, None)
        blob = Blob()
        blob.text = text
        blob.freeze()
        self.write(blob)
        index.add(path, blob.name)
        newtree = index.write()
        parent_ids = []
        if parent:
            parent_ids.append(parent)
        name = self.commit(newtree, parent_ids, changelog, author_name,
                author_email)
        return name

    def find_mergebase(self, branch1, branch2):
        """Finds the best common ancestor between the heads of two branches.
        
        Returns (current, mergebase, other), the object names of three commits.
        """
        current = self.find_head(branch1)
        other = self.find_head(branch2)
        output = self.git_command('merge-base', current, other)
        mergebase = output.rstrip()
        return (current, mergebase, other)

    # TODO: in merge, set author_name and author_email on commit
    def merge(self, branch, current, mergebase, other_commit,
            resolutions=None):
        """Merges in changes from other_commit using 3-way merge.

        Automatically resolves any trivial changes.  Returns a list of
        conflicts.

        Don't call this if merging is unnecessary or if a fast-forward merge
        would be most appropriate.  If there are any conflicts, you will need
        to come back and tell us what to do.

        Specify resolutions if you have already figured out how to resolve the
        conflicts that will arise.  This should be a dictionary mapping paths
        to contents.  We naively assume that file permissions should always
        be 100644.  Someday that may need to change.
        
        We will return a dict of any other unresolved conflicts:

        conflicts[path] = 'Text of file with conflict markers.'

        Note:
            mergebase = self.find_mergebase(self.commit, other_commit)
        """
        gitlib_res = {}
        MODE = '100644'
        for path, contents in resolutions.items():
            blob = gitlib.Blob(contents)
            self.write(blob)
            gitlib_res[path] = (blob.name, MODE)

        # IN PROGRESS:
        index = self.readtree(current)
        conflicts = index.merge(mergebase, other_commit, gitlib_res)
        if not conflicts:
            commitmsg = 'Merge made by Gitlib'
            if resolutions:
                commitmsg += ' with manual conflict resolution.'
            else:
                commitmsg += ' automatically.'

            newtree = index.write()
            parents = [current, other_commit]
            newcommit = self.commit(newtree, parents, commitmsg)
            self.save_head(newcommit, current, branch)
            return {}
        else:
            # Get rid of the "[" and "]" when we stop supporting Python 2.3:
            return dict([(c.path, c.merge_file()) for c in conflicts])


# vim: et sw=4 sts=4
