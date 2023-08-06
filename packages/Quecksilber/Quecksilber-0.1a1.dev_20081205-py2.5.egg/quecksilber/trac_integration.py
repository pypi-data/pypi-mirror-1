#!/usr/bin/env python

# -----------------------------------------------------------------------
# Copyright (c) 2008 Jan Niklas Fingerle
#
# update_ticket hook:
# Copyright (c) 2004 Stephen Hansen,
#               2008 Jan Niklas Fingerle
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

# -----------------------------------------------------------------------
# The update_ticket hook was originally written by Stephen Hansen,
# used by John Goerzen in his Commit Hooks package 
# (http://software.complete.org/software/wiki/commithooks)
# and "extracted" from this package and modified by Jan Niklas Fingerle.
# -----------------------------------------------------------------------

"""quecksilber.trac_integration - mercurial hooks for trac integration

The quecksilber subpackage trac_integration contains hooks to integrate 
mercurial repositories with trac installations.

To work, the path to the trac environment has to be configured as
entry [trac].environment in the hgrc file.
"""

import re
import email

from mercurial.node import short

from trac.env import open_environment
from trac.ticket.notification import TicketNotifyEmail
from trac.ticket import Ticket
from trac.ticket.web_ui import TicketModule
from trac.resource import ResourceNotFound

from quecksilber import _all_changectxs, _all_files_and_changectxs

SECTION_TRAC = 'trac'
SECTION_TRAC_ENTRY_ENVIRONMENT = 'environment'

SECTION_TRAC_ENTRY_UPDATE_MESSAGE = 'update_message'

TICKETPATTERN = re.compile(r'#([0-9]+)')

__all__ = ['check_mail', 'update_ticket']


def check_mail(ui, repo, node, **kwargs):
    """hg hook: check checkin user mail address in trac

    This hg hook checks for all new changesets, whether the 
    given checkin user mail address is the mail address of a 
    trac user. If not, it fails.
    """

    env, db = _get_trac_env_db(ui)
    broken = False

    for cctx in _all_changectxs(repo, node):
        _, addr = email.Utils.parseaddr(cctx.user())
        found = False

        if addr:
            for (_, _, e) in env.get_known_users(db):
                if e == addr:
                    found = True
                    break  

        if not found:
            if not broken:
                ui.warn('Committing or pushing changesets from unknown '
                        'authors:\n')
            ui.warn(' * Changeset %s: %s\n' % (str(cctx), addr))
            broken = True

    return broken


def update_ticket(ui, repo, node, **kwargs):
    """propagate hg commit messages to trac tickets

    This hg hook searches commit messages for ticket references like
    #17 or #42. The commit message will then be added as comment to the
    referenced ticket.

    The added message is configured as entry [trac].update_message.
    This entry is first 'eval'-ed and then the following strings are
    interpolated:
        %(changeset)s - the changeset ID
        %(branch)s    - the branch name
        %(tags)s      - the tag names
        %(msg)s       - the commit message

    Beware: The hgrc uses the same %(...)s interpolation strings. Therefore
    you have to write %%(...)s under all normal circumstances to give one
    of the four interpolation strings above.

    Beware #2: The python code in update_message will be evaluated, so it 
    may do any harm. However, whoever is allowed to configure this into 
    the hgrc may do any harm, anyway.
    """

    env, db = _get_trac_env_db(ui)

    for cctx in _all_changectxs(repo, node):
        author = cctx.user()
        _, addr = email.Utils.parseaddr(author)
        if addr:
            for (u, _, e) in env.get_known_users(db):
                if e == addr:
                    author = u
                    break

        msg = eval(ui.config(SECTION_TRAC, 
                        SECTION_TRAC_ENTRY_UPDATE_MESSAGE
                       )) % {"changeset": str(cctx),
                                          "branch": cctx.branch(),
                                          "tags": '; '.join(cctx.tags()),
                                          "msg": cctx.description()}

        for ticket_id in set(TICKETPATTERN.findall(cctx.description())):
            try:
                ticket = Ticket(env, int(ticket_id), db)
    
                # determine sequence number...
                cnum = 0
                tm = TicketModule(env)
                for change in tm.grouped_changelog_entries(ticket, db):
                    if change['permanent']:
                        cnum += 1

                ticket.save_changes(author, msg, db=db, cnum=cnum+1)
                db.commit()
        
                tn = TicketNotifyEmail(env)
                tn.notify(ticket, newticket=0)

            except ResourceNotFound:
                ui.warn('Referring to ticket #%s, which does not exist. '
                        'Committing anyway.\n' % ticket_id)


def _get_trac_env_db(ui):
    """return trac env and db

    This helper function opens the configured trac environment and
    data base and returns the corresponding objects.
    """

    env = open_environment(ui.config(SECTION_TRAC, 
                                     SECTION_TRAC_ENTRY_ENVIRONMENT))
    db = env.get_db_cnx()
    return env, db
