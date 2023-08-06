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

# TODO: allow filters to give errors in a meaningful way.  The best way to do
# this is probably to add HTTP return codes to filters (and cache error
# messages).  (maybe make it timeout at 5 minutes instead 30 minutes)

"""Smug content filters.

A filter is a function that takes a `file` and optional keyword args.  The
file is initialized from the source file, so a no-op filter can simply return.
The attributes of the file that are usually changed are `content` and
`mimetype`.

By the way, we don't feel bad shadowing the builtin `file` because it's going
away in Python 3.0 anyway.
"""

from smug import config

# TODO: allow filters to be chained (when filter names separated by commas).
def get_filter(using):
    """Return the filter function for `using`."""
    return FILTERS[using]


def plaintext(file, **kwds):
    """Retrieve content as-is but with mimetype text/plain."""
    
    file.mimetype = 'text/plain'


def extract_title(s):
    """Extract the title from a string.

    The title must be contained in the first line of the string and must be of
    the form:

    <!-- title: Title Goes Here -->
    """
    OPEN = "<!--"
    CLOSE = "-->"
    LABEL = "title"
    try:
        newline = s.index('\n')
        start = s.index(OPEN, 0, newline) + len(OPEN)
        end = s.index(CLOSE, start, newline)
    except ValueError:
        return ''

    comment = s[start:end]
    key, value = comment.split(':', 1)

    if key.strip().lower() != LABEL:
        return ''

    return value.strip()


def present(file, repo, **kwds):
    """Render a Django template with the content as a context variable."""

    try:
        template = kwds['template']
    except KeyError:
        template = config.basetemplate
    request = kwds['request']

    raw_content = file.content
    if not raw_content:
        return

    from django.core.urlresolvers import reverse
    baseurl = reverse('repo-%s' % repo.name, kwargs={'page': ''})
    context_dict = {'baseurl': baseurl}

    # Setup the menu of Smug actions
    from menu import SmugMenu
    menu = SmugMenu(file.path, request)
    menu.add_query('Edit', 'edit', True)
    context_dict['smugmenu'] = menu

    from django.utils.safestring import mark_safe

    context_dict['title'] = extract_title(raw_content)
    context_dict['content'] = mark_safe(raw_content)

    from django.template.loader import render_to_string
    file.content = render_to_string(template, context_dict)


def rst2html(file, repo, **kwds):
    """Render a Django template with the content as a context variable."""

    template = kwds.get('template', config.basetemplate)
    request = kwds['request']

    raw_content = file.content
    if not raw_content:
        return

    from django.core.urlresolvers import reverse
    baseurl = reverse('repo-%s' % repo.name, kwargs={'page': ''})
    context_dict = {'baseurl': baseurl}

    # Setup the menu of Smug actions
    from menu import SmugMenu
    menu = SmugMenu(file.path, request)
    menu.add_query('Edit', 'edit', True)
    context_dict['smugmenu'] = menu

    # Get HTML parts from reST
    from docutils import core
    parts = core.publish_parts(source=raw_content,writer_name='html')

    from django.utils.safestring import mark_safe
    
    context_dict['title'] = parts['title']
    context_dict['content'] = mark_safe(parts['html_body'])

    from django.template.loader import render_to_string
    file.content = render_to_string(template, context_dict)
    file.mimetype = 'text/html'


# TODO: figure out what images the latex source needs, and make them available
# to pdflatex.
def latex2pdf(file, **kwds):
    """Render a PDF from a tex template and send it to the user."""
    import subprocess, shutil, tempfile

    # TODO: Read PDFLATEX_BIN from the settings file or something.
    PDFLATEX_BIN = 'pdflatex'

    tmpdir = tempfile.mkdtemp('smugtex')
    texfile = tmpdir + '/djangotex.tex'
    pdffile = tmpdir + '/djangotex.pdf'

    # Alternatively, we could pipe the contents to LaTeX both times, but this
    # makes for easier debugging and might even be faster.
    open(texfile, 'w').write(file.content)

    # NOTE: LaTeX often needs to be run multiple times.  Here we assume it
    # needs exactly two runs.

    # pdflatex outputs 0 for good, 1 for so-so, and 255 for really bad
    args = (PDFLATEX_BIN, '-draftmode', '-interaction', 'batchmode', texfile)
    retcode = subprocess.call(args, cwd=tmpdir)
    if retcode != 0 and retcode != 1:
        #raise PDFLatexFailed
        return

    args = (PDFLATEX_BIN, '-interaction', 'batchmode', texfile)
    retcode = subprocess.call(args, cwd=tmpdir)
    if retcode != 0 and retcode != 1:
        #raise PDFLatexFailed
        return

    file.content = open(pdffile, 'r').read()
    file.mimetype = 'application/pdf'

    # TODO: make a config option that determines whether or not to do the
    # rmtree (sometimes you need the files for debugging):
    shutil.rmtree(tmpdir)


def rst2latex(file, **kwds):
    """Render a ReST source file as a latex source document."""

    raw_content = file.content
    if not raw_content:
        return

    file.mimetype = "application/x-latex"

    # Get latex from reST
    from docutils import core
    file.content = core.publish_string(source=raw_content, writer_name='latex')


# TODO: Do proper nested filters.
def rst2latex2pdf(file, **kwds):
    """Render a ReST source file as a latex-generated pdf document."""

    # First, render the latex source file.
    rst2latex(file, **kwds)
    # Then render the pdf.
    latex2pdf(file, **kwds)


def plot2png(file, **kwds):
    """Render a gnuplot script as a png image."""

    from subprocess import Popen, PIPE

    REMOVE = 'set terminal'
    INSERT = 'set terminal png'

    original = file.content.splitlines()
    script = [INSERT]
    script += [line for line in original if not line.startswith(REMOVE)]

    proc = Popen(('gnuplot',), stdin=PIPE, stdout=PIPE)
    proc.stdin.write('\n'.join(script))
    proc.stdin.close()
    proc.wait()
    file.content = proc.stdout.read()
    file.mimetype = "image/png"


FILTERS = dict([(f.__name__, f) for f in (plaintext, present, rst2html,
        rst2latex, rst2latex2pdf, plot2png)])

# vim: et sw=4 sts=4
