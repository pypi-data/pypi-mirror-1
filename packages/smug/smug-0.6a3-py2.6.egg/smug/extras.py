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

"""Template helpers for Django."""

BRANCH = 'master'
PROTOCOL = 'smug://'

from django.template import TemplateDoesNotExist
from django.conf import settings
#from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseRedirect
import config

def smug_load_template_source(template_name, template_dirs=None):
    """Extract a template from the Git repository"""

    import os
    if template_dirs is None:
        template_dirs = settings.TEMPLATE_DIRS

    for template_dir in template_dirs:
        if template_dir.startswith(PROTOCOL):
            repokey, subdir = template_dir[len(PROTOCOL):].split('/', 1)
            repo = config.repositories[repokey]

            path = '/'.join((subdir, template_name))
            name = repo.getname(path, BRANCH)
            blob = repo.getblob(name)
            if blob is not None:
                full_url = '/'.join((template_dir, path))
                return blob.contents, full_url
    raise TemplateDoesNotExist(template_name)

smug_load_template_source.is_usable = True


try:
    http_base = settings.HTTP_BASEURL
except AttributeError:
    http_base = 'http://'

try:
    https_base = settings.HTTPS_BASEURL
except AttributeError:
    https_base = 'https://'

def ssl_redirect(request, ssl=True):
    """Redirect to https if ssl=True or to http if ssl=False.

    The values configured in settings.py as HTTP_BASEURL and HTTPS_BASEURL
    are required if they differ in any way other than "http" vs. "https".
    """
    if (ssl is None) or (ssl == request.is_secure()):
        return None

    old_uri = request.build_absolute_uri()

    if ssl and old_uri.startswith(http_base):
        # Redirect to https
        new_uri = https_base + old_uri[len(http_base):]
    elif (not ssl) and old_uri.startswith(https_base):
        # Redirect to http
        new_uri = http_base + old_uri[len(https_base):]
    else:
        raise RuntimeError("Base URLs are inconsistent in ssl_redirect()")

    #return HttpResponsePermanentRedirect(new_uri)
    return HttpResponseRedirect(new_uri)


class SecureSessionMiddleware(object):
    """Redirect paths between http and https as requested by urlpatterns.
    
    Check for 'secure' in a view's kwargs.  If not set or None, do nothing.
    If True, redirect to https if secure sessions are requested.  If False,
    redirect to http.

    The values configured in settings.py as HTTP_BASEURL and HTTPS_BASEURL
    are required if they differ in any way other than "http" vs. "https".
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            ssl = view_kwargs['session']
            del view_kwargs['session']
        except KeyError:
            ssl = None

        if settings.SESSION_COOKIE_SECURE:
            return ssl_redirect(request, ssl)
        else:
            return None

# vim: et sw=4 sts=4
