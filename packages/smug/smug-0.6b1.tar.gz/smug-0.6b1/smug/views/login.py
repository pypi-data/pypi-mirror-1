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

"""Login form.

Note that this is different from Django's login form because we need to be
do SSL session redirecting, and Django's form breaks it.
"""

from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.contrib import auth
from django.contrib.auth import forms, REDIRECT_FIELD_NAME

LOGIN_TEMPLATE = 'login.html'

# TODO: make it so the name doesn't conflict with auth.login
def login(request, **kwds):
    redirect = request.REQUEST.get(REDIRECT_FIELD_NAME, '')

    if request.POST:
        f = forms.AuthenticationForm(request=request, data=request.POST)
        if f.is_valid():
            # check from django auth: "make sure redirect isn't garbage:"
            if not redirect or '//' in redirect or ' ' in redirect:
                return HttpResponseBadRequest('Invalid redirect.')
            auth.login(request, f.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return HttpResponseRedirect(redirect)
    else:
        f = forms.AuthenticationForm()

    request.session.set_test_cookie()

    context = {'form': f, REDIRECT_FIELD_NAME: redirect}
    return render_to_response(LOGIN_TEMPLATE, context)

# vim: et sw=4 sts=4
