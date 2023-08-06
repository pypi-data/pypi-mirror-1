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

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib import auth

LOGOUT_TEMPLATE = 'logout.html'

def logout(request, **kwds):
    auth.logout(request)

    redirect = request.REQUEST.get(auth.REDIRECT_FIELD_NAME, '')
    if redirect:
        return HttpResponseRedirect(redirect)
    else:
        return render_to_response(LOGOUT_TEMPLATE, {})


# vim: et sw=4 sts=4
