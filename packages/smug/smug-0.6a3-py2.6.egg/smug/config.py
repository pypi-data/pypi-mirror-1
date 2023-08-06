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

DEFAULT_TEMPLATE = 'template.html'
DEFAULT_CACHE_TIME = 30 * 60
DEFAULT_HEAD_TIMEOUT = 20
# An alternative DEFAULT_MIMETYPE would be application/octet-stream
DEFAULT_MIMETYPE = 'text/plain'
DEFAULT_ADMIN_URL = '/admin/'

from django.conf import settings
import gitlib

def _get_setting(name, default):
    try:
        return getattr(settings, name)
    except AttributeError:
        return default

# Setup revsys
repositories = {}
try:
    SMUG_REPOSITORIES = settings.SMUG_REPOSITORIES
except AttributeError:
    SMUG_REPOSITORIES = None
if SMUG_REPOSITORIES:
    for name, path in SMUG_REPOSITORIES.iteritems():
        repo = gitlib.Repository(path)
        repositories[name] = repo
        repo.name = name
    del repo

basetemplate = _get_setting('SMUG_TEMPLATE', DEFAULT_TEMPLATE)

# How long to cache an ordinary page.
cache_time = _get_setting('SMUG_CACHE_TIME', DEFAULT_CACHE_TIME)
# How long to cache the head ref.
head_timeout = _get_setting('SMUG_HEAD_TIMEOUT', DEFAULT_HEAD_TIMEOUT)
# Admin directory (note, None means admin not installed)
admin_url = _get_setting('ADMIN_URL', DEFAULT_ADMIN_URL)

# vim: et sw=4 sts=4
