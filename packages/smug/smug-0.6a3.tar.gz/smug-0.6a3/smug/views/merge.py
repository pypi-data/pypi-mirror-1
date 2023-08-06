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

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django import forms

from smug.config import basetemplate, repositories


class MergePrepForm(forms.Form):
    """Form for first part of merge."""
    branch1 = forms.CharField(label='Branch to Merge Into')
    branch2 = forms.CharField(label='Branch to Merge From')
    do_merge = forms.CharField(widget=forms.widgets.HiddenInput)

class ConflictForm(forms.Form):
    """Form for first part of merge."""
    branch1 = forms.CharField(widget=forms.widgets.HiddenInput)
    branch2 = forms.CharField(widget=forms.widgets.HiddenInput)
    current = forms.CharField(widget=forms.widgets.HiddenInput)
    mergebase = forms.CharField(widget=forms.widgets.HiddenInput)
    other = forms.CharField(widget=forms.widgets.HiddenInput)
    do_merge = forms.CharField(widget=forms.widgets.HiddenInput)

def merge(request, repo=None, **kwds):
    """Attempt to merge any missing commits from one branch into another.

    URL looks like:
        http://smug/!merge?from=branch2&into=branch1
    Normal users will usually do:
        http://smug/!merge?from=master&into=username/mybranch
    in order to bring mybranch up-to-date.  Editors will usually do:
        http://smug/!merge?from=someuser/somebranch&into=master
    in order to incorporate a user's changes into the mainstream.

    We will attempt to do a a trivial merge.  If there are conflicts, we
    will redirect the user to a conflict resolution page, the details of
    which are not yet known.
    """
    if repo is None:
        raise RuntimeError('URLs configuration error.  No repo specified.')
    repo = repositories[repo]

    branch1 = request.GET.get('branch1', '')
    branch2 = request.GET.get('branch2', '')
    # If branches are specified in POST, they override those from GET:
    branch1 = request.POST.get('branch1', branch1)
    branch2 = request.POST.get('branch2', branch2)

    current = request.POST.get('current', '')
    other = request.POST.get('other', '')
    mergebase = request.POST.get('mergebase', '')

    # See if the MergePrepForm has already been filled out:
    try:
        request.POST['do_merge']
        do_merge = True
    except KeyError:
        do_merge = False

    if not branch1 or not branch2:
        do_merge = False
    # TODO: Make sure that both branches exist, if given.

    if do_merge:
        if not current or not mergebase or not other:
            current, mergebase, other = repo.prep_merge(branch1, branch2)

        if mergebase == other:
            return HttpResponse("Nothing to do (we're newer than the other branch.")

        # It turns out that 3-way merge is a slow way of doing a fast-forward
        # merge in this case.  We should still probably implement the
        # fast-forward merge, though, because that way the merge wouldn't add
        # an extra commit message into the logs.
        #elif mergebase == current:
            #return HttpResponse('We need to do a fast-forward merge.')

        # See if we can do the merge as-is:
        resolutions = {}
        for key, contents in request.POST.items():
            if key.startswith('conflict_'):
                path = key.replace('conflict_', '', 1)
                resolutions[path] = contents
        new_conflicts = repo.merge(branch1, current, mergebase, other,
                resolutions)

        if new_conflicts:
            return HttpResponse('Conflicts form goes here.')
        else:
            return HttpResponse('Merge successful: branch1=%s.' % branch1)
        # End with an HttpResponseRedirect
    else:
        # Present the user with an explanation of what is about to happen
        # and give them a "Merge" button.

        # TODO: Maybe we should show a picture of how the branches relate a la
        # gitk on this page.

        form_vars = {'do_merge': 'do_merge',
                'branch1': branch1, 'branch2': branch2}
        form = MergePrepForm(initial=form_vars)

        title = 'Merge from branch "%s" into branch "%s"' % (branch2, branch1)
        page_vars = {'title': title, 'form': form,
                'submit_label': 'Merge',
                'basetemplate': basetemplate}
        return render_to_response('smugform.html', page_vars)

# vim: et sw=4 sts=4
