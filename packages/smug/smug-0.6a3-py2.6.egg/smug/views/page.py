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

DEFAULT_BRANCH = 'master'

from django.http import HttpResponseBadRequest
from smug import config
from smug.pathops.edit import edit
from smug.pathops.raw import raw
from smug.pathops.show import show

PATHOPS = {'edit': edit}

def page(request, page=None, repo=None):
    if repo is None:
        raise RuntimeError('URLs configuration error.  No repo specified.')
    repo = config.repositories[repo]

    branch = request.GET.get('branch', DEFAULT_BRANCH)
    pathop = None
    for name, func in PATHOPS.iteritems():
        if name in request.GET:
            if pathop:
                return HttpResponseBadRequest()
            else:
                pathop = func

    if pathop is None:
        pathop = show

    return pathop(request, page, repo, branch)


# vim: et sw=4 sts=4
