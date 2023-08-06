#!/usr/bin/env python

# -----------------------------------------------------------------------
# Copyright (c) 2008 Jan Niklas Fingerle
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the 
# "Software"), to deal in the Software without restriction, including 
# without limitation the rights to use, copy, modify, merge, publish, 
# distribute, sublicense, and/or sell copies of the Software, and to 
# permit persons to whom the Software is furnished to do so, subject to 
# the following conditions:
#
#   The above copyright notice and this permission notice shall be 
#   included in all copies or substantial portions of the Software. 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------

"""quecksilber - mercurial hook package

The python quecksilber (German for mercury) package contains some
small mercurial hooks. There's also a subpackage 
quecksilber.trac_integration that contains hook for repositories that are
connected to a trac installation.
"""

import re
import mercurial.commands
from mercurial.node import bin, hex, short

SECTION_CHANGESET = 'changeset'
SECTION_CHANGESET_ENTRY_BLACKLIST = 'blacklist'

SECTION_BRANCH = 'branch'
SECTION_BRANCH_ENTRY_NAME = 'name'
    
SECTION_FILE_CHECK = 'file_content_check' 
SECTION_FILE_CHECK_ENTRY_EXTENSIONS = 'extensions'

__all__ = ['blacklist_changeset', 'one_head', 'branch_name', 
           'file_content_check', 'fail']


def blacklist_changeset(ui, repo, node, **kwargs):
    """hg hook: check checked in hg changesets against blacklist

    This hg hook checks wether one of the new changesets is
    blacklisted and fails if necessary. The blacklist is 
    a whitespace separated list of hexadecimal node ids 
    configured in entry [changeset].blacklist of the hgrc file.
    """
    blacklist = ui.config(SECTION_CHANGESET, 
                          SECTION_CHANGESET_ENTRY_BLACKLIST).split()

    broken = False

    for this_node in (hex(cctx.node()) for cctx in _all_changectxs(repo, node)):
        if this_node in blacklist:
            if not broken:
                ui.warn('You are trying to commit (a) blacklisted '
                        'changeset(s):\n')
            ui.warn('  - %s\n' % this_node)
            broken = True

    return broken


def one_head(ui, repo, node, **kwargs):
    """hg hook: check, if there is only one head in the repository

    This hg hook checks, if there is more than one head in the 
    repository. If so, it fails.
    """

    if len(repo.heads()) > 1:
        ui.warn('Action will result in multiple heads. '
                'This is not allowed.\n')
        return True
    return False


def branch_name(ui, repo, node, **kwargs):
    """hg hook: check, if all heads are members of a given branch

    This hg hooks checks, if all heads are members of a given
    branch. If not, it fails. The branch name is configured in 
    entry [branch].name of the hgrc file.

    """

    broken = False
    branch = ui.config(SECTION_BRANCH, SECTION_BRANCH_ENTRY_NAME)
    for head in repo.heads():
        c = repo.changectx(head)
        if c.branch() != branch:
            if not broken:
                ui.warn('One or more head(s) is not named "%s":\n' % branch)
            ui.warn('  - changeset %s: "%s"\n' % (str(c), c.branch()))
            broken = True
    return broken


def file_content_check(ui, repo, node, **kwargs):
    """hg hook: check, if files contain some kind of 'bad' content

    This hg hook checks, if any file in any of the new changesets 
    contains 'bad' content, and fails if needed.

    Checked file extensions are configured as whitespace separated
    list (without dot) in entry [file_content_check].extensions
    of the hgrc file. For each extension <ext> there has to be
    an additional entry [file_content_check].<ext> with a
    multiline regular expression pattern in python code. The check 
    fails if this pattern matches, i. e. the pattern specifies _bad_ 
    content.

    Beware: The python code for the regular expression will be
    evaluated, so it may do any harm. However, whoever is allowed to 
    configure this into the hgrc may do any harm, anyway.

    Example for python (*.py) files that should not contain TAB
    characters for indentation:

    [file_content_check]
    extensions = py
    py = r"^ *\t"

    """

    broken = False

    pattern = {}
    for ext in ui.config(SECTION_FILE_CHECK, 
                         SECTION_FILE_CHECK_ENTRY_EXTENSIONS).split():
        pattern[ext] = re.compile(eval(ui.config(SECTION_FILE_CHECK, 
                                                 ext)), re.MULTILINE)

    for file_, cctx in _all_files_and_changectxs(repo, node):
        file_ext = file_.split('.')[-1]
        
        if file_ext in pattern.keys():
            if pattern[file_ext].match(cctx[file_].data()):
                if not broken:
                    ui.warn('Some files do match the bad file content ' 
                            'regular expression:\n')
                ui.warn('  - node %s, file %s\n' % (str(cctx), file_))
                broken = True

    return broken


def only_push(ui, source, **kwargs):
    """hg hook: fail, if repository is pulled

    This hg hook fails if the repository is pulled. Changeset may
    leave the repository only by push.
    """
    
    if source == 'push':
        return False
    else:
        ui.warn('This operation is not allowed.\n')
        return True


def _all_changectxs(repo, node):
    """yield all change contexts for a given repo and starting node
    
    This helper function yields all "new" changes (as change
    contexts) for a given hg repository 'repo' and a starting
    node 'node'. These are the same 'repo' and 'node' as are
    given to hg hooks.
    """

    for rev in range(repo.changelog.rev(bin(node)), repo.changelog.count()):
        yield repo.changectx(rev)


def _all_files_and_changectxs(repo, node):
    """yield all new or changed files and their change context(s) 
    for a given repo and starting node
    
    This helper function yields all new or changed files with corresponding
    change contexts in all "new" changes for a given hg repository 'repo' 
    and a starting node 'node'. These are the same 'repo' and 'node' as are
    given to hg hooks.
    """

    for cctx in _all_changectxs(repo, node):
        for file_ in cctx.files():
            if file_ not in cctx:
                continue
            yield file_, cctx
    
