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
from django.contrib.auth.decorators import login_required
from django import forms

from smug import config
from smug.load import get_source, HeadCache


class AnonymousEditForm(forms.Form):
    """Edit form for anonymous users."""
    text = forms.CharField(widget=forms.widgets.Textarea(
            attrs={'cols': 80, 'rows': 24}))
    changelog = forms.CharField(widget=forms.widgets.Textarea(
            attrs={'cols': 80, 'rows': 3}))
    parent = forms.CharField(widget=forms.widgets.HiddenInput)
    noeol = forms.CharField(widget=forms.widgets.HiddenInput)


class AuthenticatedEditForm(AnonymousEditForm):
    """Edit form for authenticated users.
    
    Unlike anonymous users, authenticated users can pick a branch to commit to.
    """

    # TODO: make a radio button: "commit in place" vs. "start new branch."
    # They can only commit in place if they have write-access to the branch
    # (i.e. they're either an editor or they own the branch).  Maybe even
    # give the option to automatically pick the name for the new branch.
    branch = forms.CharField(label='Commit to Branch')


def edit(request, page, repo, branch, **kwds):
    """Edit a page in the wiki.

    This function both displays the form and processes its results.
    """
    source_file, filter, filter_args  = get_source(page, branch, repo)
    path = source_file.sourcepath
    if not path:
        path = page

    user = request.user

    if request.method == 'POST':
        text = request.POST['text'].encode('utf-8')
        changelog = request.POST['changelog'].encode('utf-8')
        parent = request.POST['parent']
        if request.POST['noeol'] == 'False':
            text = text + '\n'

        # Normalize whitespace--use Unix newlines:
        text = text.replace('\r\n', '\n')

        if user.is_authenticated():
            # Get branch and parent from form
            newbranch = request.POST['branch']

            success = commit_auth(user, path, parent, changelog, text,
                    newbranch, repo)

            if not success:
                # TODO: Do something better than just return.  Perhaps we
                # should try to do a fast-forward merge or recommend that they
                # create a new branch and merge or something else completely.
                # Or maybe the commit succeeded earlier, and they just
                # reposted it.
                return HttpResponse('Commit failed!')
        else:
            commit_anon(path, branch, changelog, text)

        if newbranch == 'master':
            redirect = request.path
        else:
            redirect = '%s?branch=%s' % (request.path, newbranch)
        return HttpResponseRedirect(redirect)
    else:
        # Supply a page with an edit form
        return edit_form(path, branch, repo, user)


def commit_auth(user, path, parent, changelog, text, newbranch, repo):
    """Commit changes as an authenticated user."""

    # Set name and email for Git commit
    if user.first_name and user.last_name:
        author_name = ' '.join((user.first_name, user.last_name))
    else:
        author_name = user.username
    if user.email:
        author_email = user.email
    else:
        author_email = None

    # TODO: it's probably smart to do a fast-forward merge here when the
    # branch has moved ahead of us and parent != currenthead.  Here's how that
    # looks:
    # 1) do git-add on the changes that the person made
    # 2) do a "git-merge -m parent -m newhead"
    # 3) do a commit and save_head
    # If the save_head command fails, maybe the smart thing to do is to try to
    # repeat this whole process a few times in a row.

    newcommit = repo.commit_add(path, text, parent, changelog,
            author_name, author_email)

    # This will fail if the new commit is not a child of the current head or
    # if the current head changes on us while we are committing:
    success = repo.save_head(newcommit, parent, newbranch)
    if success:
        head_cache = HeadCache(repo, newbranch)
        head_cache.update(newcommit)

    return success


def commit_anon(path, parent, changelog, text):
    """Commit changes as an anonymous user."""

    from difflib import unified_diff
    from smug.models import Patch

    # Retrieve old text.
    name = repo.getname(path, treename=parent)
    blob = repo.getblob(name)
    if blob is None:
        # TODO: Fail here in a better way.
        raise Http404

    patch = Patch()
    patch.status = 's'
    patch.parent = parent
    patch.changelog = changelog

    fromfile = '%s.%s' % (path, parent)
    udiff = unified_diff(blob.contents.splitlines(), text.splitlines(),
            fromfile=fromfile, tofile=path, lineterm='')
    patch.diff = '\n'.join(udiff)
    patch.save()


def edit_form(path, branch, repo, user):
    """Supply a page with an edit form."""

    # FIXME: We should be doing find_head directly.
    head = repo.find_head(branch)
    name = repo.getname(path, treename=head)
    if name:
        blob = repo.getblob(name)
        text = blob.contents
    else:
        text = ''

    if text and text[-1] == '\n':
        noeol = "False"
        text = text[0:-1]
    else:
        noeol = True

    form_vars = {'text': text, 'parent': head, 'noeol': noeol}
    page_vars = {'basetemplate': config.basetemplate}

    if user.is_authenticated():
        form_vars['branch'] = branch
        page_vars['submit_label'] = 'Commit'
        page_vars['title'] = 'Edit "%s" from branch "%s"' % (path, branch)
        form = AuthenticatedEditForm(initial=form_vars)
    else:
        page_vars['submit_label'] = 'Submit Patch'
        page_vars['title'] = 'Anonymously Edit "%s"' % (path)
        form = AnonymousEditForm(initial=form_vars)

    page_vars['form'] = form
    return render_to_response('smugform.html', page_vars)


# vim: et sw=4 sts=4
