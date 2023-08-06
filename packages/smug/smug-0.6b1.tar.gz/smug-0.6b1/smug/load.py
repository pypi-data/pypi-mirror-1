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

"""Load and filter files from the Git repository or cache."""


def dotsmug_paths(path):
    """Make a list of the .smug files that should be loaded for a given path.

    >>> dotsmug_paths('path/to/file')
    ['path/to/.smug', 'path/.smug', '.smug']
    >>> dotsmug_paths('path/to/dir/')
    ['path/to/dir/.smug', 'path/to/.smug', 'path/.smug', '.smug']
    >>>
    """
    path_splits = path.split('/')[:-1]

    subpaths = ['']
    for split in path_splits:
        next = subpaths[-1] + split + '/'
        subpaths.append(next)

    results = [(subpath + '.smug') for subpath in subpaths]
    results.reverse()

    return results


def load_dotsmug(request_path, repo):
    """Load the .smug config file as a dotsmug.Config."""

    from dotsmug import DotSmug, Config

    paths = dotsmug_paths(request_path)
    rawfiles = [SourceFile(path, 'master', repo) for path in paths]
    dotsmugs = [DotSmug(raw.content) for raw in rawfiles if raw.exists()]

    config = Config(dotsmugs)
    return config


def get_source(path, branch, repo):
    """Gets the source file and filter for the given request path.
    
    The .smug settings are used to determine the source path from the request
    path.

    Returns (source_file, filter, filter_args).
    """
    # Load configuration:
    dotsmug = load_dotsmug(path, repo)

    if not path or path.endswith('/'):
        index = dotsmug.directory_index()
        if index:
            path += index

    for source_path, using in dotsmug.convert_sources(path):
        source_file = SourceFile(source_path, branch, repo)
        if source_file.exists():
            from filters import get_filter
            filter = get_filter(using)
            break
    else:
        source_file = SourceFile(path, branch, repo)
        source_path = path
        filter = None

    filter_args = {}
    template = dotsmug.template()
    if template:
        filter_args['template'] = template

    return source_file, filter, filter_args


def get_content(request_path, branch, repo, raw=False, **filter_args):
    """Gets a file from the Git repo, using a cache if possible."""
    if raw:
        dest_file = SourceFile(request_path, branch, repo)
    else:
        dest_file = FilteredFile(request_path, branch, repo, filter_args)

    if not dest_file.exists():
        from django.http import Http404
        raise Http404

    return dest_file


# TODO: Update merging, etc., to update the head ref as they write to the repo.
class HeadCache(object):
    """Accesses and updates the cached reference to the head of a branch."""

    def __init__(self, repo, branch='master'):
        self.key = 'head:%s(%s)' % (repo.path, branch)
        self.repo = repo
        self.branch = branch

    def get(self):
        """Gets the commit id of the head of the given branch."""
        from django.core.cache import cache
        head = cache.get(self.key)
        if head is None:
            #print 'cache miss for head:', self.key
            head = self.update()
        return head

    def update(self, head=None):
        """Update the cached head ref from a specified value or from disk.

        Note that it's possible to accidentally set the head ref to an older
        value, but the head ref will never be more than than `head_timeout`
        seconds old.
        """
        import config
        from django.core.cache import cache
        if head is None:
            head = self.repo.find_head(self.branch)
        cache.set(self.key, head, config.head_timeout)
        return head


def cached_property(name):
    """A property that forces a self.lookup() call when read.
    
    The given name is the name of the cached variable (usually starting with
    an underscore).
    """
    def getter(self):
        if self.delayed:
            self.lookup()
        return getattr(self, name)
    def setter(self, value):
        setattr(self, name, value)
    return property(getter, setter)


class CachedFile(object):
    """Raw or filtered content.

    Smug will try to cache data as much as possible, so all requests to the
    repository should try to go through CachedFile.
    """

    KEY_PREFIX = None

    def __init__(self, path, branch, repo):
        self.path = path
        self.branch = branch
        self.repo = repo
        self.key = '%s:%s//%s(%s)' % (self.KEY_PREFIX, repo.path, path, branch)
        self.head_cache = HeadCache(repo, branch)

        # If delayed is set, information has not yet been retrieved/generated.
        self.delayed = True

        self._commit = None
        self._type = None
        self._mimetype = None
        self._content = None
        self._sourcename = None
        self._sourcepath = None

    def is_directory(self):
        if self.delayed:
            self.lookup()
        return self._type == 'tree'

    def exists(self):
        if self.delayed:
            self.lookup()
        return self._type is not None

    def source_file(self):
        raise NotImplementedError

    def lookup(self):
        """Try to find all information, either from the cache or from Git."""
        from django.core.cache import cache
        values = cache.get(self.key)
        self.delayed = False

        if values:
            (self.commit, self.type, self.mimetype, self.content,
                    self.sourcename, self.sourcepath) = values
            head = self.head_cache.get()
            if self.commit == head:
                #print 'cache hit for:', self.key
                loaded = True
            else:
                # The cache is out of date but might still be correct.
                #print 'cache miss (outdated commit) for:', self.key
                self.commit = None
                loaded = False
        else:
            # Cache miss
            #print 'cache miss for:', self.key
            (self.commit, self.type, self.mimetype, self.content,
                    self.sourcename, self.sourcepath) = (None,) * 6
            loaded = False

        if not loaded:
            self.retrieve()
            # TODO: only cache on success?
            self.cache_data()

    def cache_data(self):
        """Save data to the cache."""
        from django.core.cache import cache
        values = (self._commit, self._type, self._mimetype, self._content,
                self._sourcename, self._sourcepath)
        cache.set(self.key, values)

    def retrieve(self):
        """Try to retrieve content from the actual source.

        This must be implemented by subclasses.
        """
        raise NotImplementedError

    def dirty(self):
        """Clear information from the cache."""
        #print 'trying to dirty cache for "%s"' % self.key
        from django.core.cache import cache
        cache.delete(self.key)
        self.delayed = True

    commit = cached_property('_commit')
    content = cached_property('_content')
    type = cached_property('_type')
    mimetype = cached_property('_mimetype')
    sourcename = cached_property('_sourcename')
    sourcepath = cached_property('_sourcepath')


class SourceFile(CachedFile):
    """A file from a Git repository."""

    KEY_PREFIX = 'source'

    def source_file(self):
        return self

    def retrieve(self):
        """Try to retrieve content from the Git repository.

        If there was a complete cache miss, the object properties (commit,
        sourcename, etc.) will be None before retrieve is called.  If there
        was an outdated cache hit, then self.commit will be None but the rest
        of the properties will be set to the cached values.
        """
        commit = self.head_cache.get()
        name = self.repo.getname(self.path, treename=commit)
        if not name:
            # TODO: cache nonexistent files (?)
            return

        # Check for an outdated but valid cache hit.
        if not self.commit and self.sourcename and (self.sourcename == name):
            self.commit = commit
            return

        self.sourcename = name
        self.commit = commit
        self.type = self.repo.gettype(name)
        if self.type == 'blob':
            blob = self.repo.getblob(name)
            self.content = blob.contents
            self.sourcepath = self.path

            from mimetypes import guess_type
            self.mimetype, encoding = guess_type(self.path, strict=False)


class FilteredFile(CachedFile):
    """Filtered content.

    For now, this will handle all filtered content.  In the future, it will
    only handle Djangoized content.
    """

    KEY_PREFIX = 'filtered'

    def __init__(self, path, branch, repo, filter_args):
        CachedFile.__init__(self, path, branch, repo)
        self.filter_args = filter_args

    def source_file(self):
        return SourceFile(self.sourcepath, self.branch, self.repo)

    def retrieve(self):
        source_file, filter, filter_args = get_source(self.path, self.branch,
                self.repo)
        if not source_file.exists():
            return

        # Check for an outdated but valid cache hit.
        if not self.commit and self.sourcename:
            if (self.sourcename == source_file.sourcename):
                self.commit = source_file.commit
                return

        self.commit = source_file.commit
        self.content = source_file.content
        self.type = source_file.type
        self.mimetype = source_file.mimetype
        self.sourcepath = source_file.sourcepath

        # Guess mimetype for extensionless files before sending on to filter.
        # Note that we don't do this in SourceFile.retrieve because then
        # load_dotsmug would get in an infinite loop.  The open question
        # though, is whether it is more appropriate to set the mimetype based
        # on self.path or self.sourcepath.
        if not self.mimetype:
            dotsmug = load_dotsmug(self.path, self.repo)
            default_mimetype = dotsmug.default_mimetype()
            if default_mimetype:
                self.mimetype = default_mimetype
            else:
                import config
                self.mimetype = config.DEFAULT_MIMETYPE

        if filter:
            # TODO: allow filters to be chained (and only cache the last one)
            kwds = self.filter_args.copy()
            kwds.update(filter_args)
            filter(self, repo=self.repo, **kwds)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

# vim: et sw=4 sts=4
