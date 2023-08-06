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

"""Smug Admin URLs.

These URLs are used once for an entire Smug installation.
"""

from views.login import login
from views.logout import logout
from views.merge import merge
from views.page import page
from django.conf.urls.defaults import *


def smugurl(pattern, repo=None):
    """Defines a per-repository URL pattern.

    Works around the brittleness of Django's include() and named urls.
    """
    if not repo:
        raise RuntimeError('Repository must be specified in smugurl.')

    new_pattern = pattern + r'(?P<page>.*)$'
    kwargs = {'session': False, 'repo': repo}
    return (new_pattern, page, kwargs, 'repo-%s' % repo)


urlpatterns = patterns('',
    url(r'^login$', login, name='smug-login',
        kwargs={'session': True, 'template_name': 'login.html'}),
    url(r'^logout$', logout, name='smug-logout',
        kwargs={'session': True, 'template_name': 'logout.html'}),
    url(r'^merge$', merge, name='smug-merge',
        kwargs={'session': True}),
    )

# vim: et sw=4 sts=4
