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

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from itertools import chain
import config

class SmugMenu(object):
    """Manage a menu of Smug actions.
    
    The `page` attribute holds the current request's path within the
    repository, while the `path` attribute holds the request's path on the
    site.
    """
    def __init__(self, page, request):
        self.items = []
        self.lastitems = []
        self.page = page
        self.path = request.path

        self.authenticated = request.user.is_authenticated()

        if self.authenticated:
            # place the logout button
            # TODO: make this configurable
            # note: if you leave off the redirect, it will do a logout page
            logout_url = reverse('smug-logout')
            url = '%s?%s=%s' % (logout_url, REDIRECT_FIELD_NAME, self.path)
            self.lastitems.append(('Logout(%s)' % (request.user.username), url))
            # place the admin button
            if config.admin_url is not None:
                self.lastitems.append(('Admin', config.admin_url))
        else:
            login_url = reverse('smug-login')
            url = '%s?%s=%s' % (login_url, REDIRECT_FIELD_NAME, self.path)
            self.lastitems.append(('Login', url))

    def add_abs(self, name, url, auth=False):
        """Add a Smug action with absolute url.
        
        Specify a name, url, and whether authentication is required.
        """
        if not auth or self.authenticated:
            self.items.append((name, url))

    def add_query(self, name, query, auth=False):
        """Add a Smug action that adds a query to the current page.

        Specify a name, query, and whether authentication is required.  The
        query is of the form "key1=value1&key2=value2".
        """
        if not auth or self.authenticated:
            self.items.append((name, '?'.join((self.path, query))))

    def __iter__(self):
        return chain(self.items, self.lastitems)

# vim: et sw=4 sts=4
