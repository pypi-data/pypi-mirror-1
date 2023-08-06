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

from django import http
from django.conf import settings
from smug.load import get_content

def show(request, page, repo, branch, raw=False, **kwds):
    """Render a page straight from Git."""
    filtered_file = get_content(page, branch, repo, raw=raw, request=request)

    if filtered_file.is_directory():
        if page and not page.endswith('/'):
            return http.HttpResponseRedirect(page + '/')
        else:
            # TODO: add a configuration option for generated directory
            # indexes (in which case this would not be a 404).
            raise http.Http404

    if filtered_file.mimetype.startswith('text/'):
        content_type = '%s; charset=%s' % (filtered_file.mimetype,
                settings.DEFAULT_CHARSET)
    else:
        content_type = filtered_file.mimetype
    response = http.HttpResponse(content_type=content_type)
    # note: Python 2.4 has no rpartition
    #dirname, slash, filename = page.rpartition('/')
    split = page.rsplit('/', 1)
    if len(split) == 2:
        dirname, filename = split
    else:
        dirname = filename = ''
    response['Content-Disposition'] = 'inline; filename=%s' % filename
    response.write(filtered_file.content)
    return response


# vim: et sw=4 sts=4
