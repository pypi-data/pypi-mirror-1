# Copyright (C) 2001-2008 by the Free Software Foundation, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

"""Creation/deletion hooks for manual /etc/aliases files."""

import sys
import email.Utils

from cStringIO import StringIO

from mailman import Message
from mailman import Utils
from mailman.MTA.Utils import makealiases
from mailman.configuration import config
from mailman.i18n import _
from mailman.queue import Switchboard



# no-ops for interface compliance
def makelock():
    class Dummy:
        def lock(self):
            pass
        def unlock(self, unconditionally=False):
            pass
    return Dummy()


def clear():
    pass



# nolock argument is ignored, but exists for interface compliance
def create(mlist, cgi=False, nolock=False, quiet=False):
    if mlist is None:
        return
    listname = mlist.internal_name()
    fieldsz = len(listname) + len('-unsubscribe')
    if cgi:
        # If a list is being created via the CGI, the best we can do is send
        # an email message to mailman-owner requesting that the proper aliases
        # be installed.
        sfp = StringIO()
        if not quiet:
            print >> sfp, _("""\
The mailing list '$listname' has been created via the through-the-web
interface.  In order to complete the activation of this mailing list, the
proper /etc/aliases (or equivalent) file must be updated.  The program
'newaliases' may also have to be run.

Here are the entries for the /etc/aliases file:
""")
        outfp = sfp
    else:
        if not quiet:
            print _("""\
To finish creating your mailing list, you must edit your /etc/aliases (or
equivalent) file by adding the following lines, and possibly running the
'newaliases' program:
""")
        print _("""\
## $listname mailing list""")
        outfp = sys.stdout
    # Common path
    for k, v in makealiases(mlist):
        print >> outfp, k + ':', ((fieldsz - len(k)) * ' '), v
    # If we're using the command line interface, we're done.  For ttw, we need
    # to actually send the message to mailman-owner now.
    if not cgi:
        print >> outfp
        return
    siteowner = Utils.get_site_noreply()
    # Should this be sent in the site list's preferred language?
    msg = Message.UserNotification(
        siteowner, siteowner,
        _('Mailing list creation request for list $listname'),
        sfp.getvalue(), config.DEFAULT_SERVER_LANGUAGE)
    msg.send(mlist)



def remove(mlist, cgi=False):
    listname = mlist.fqdn_listname
    fieldsz = len(listname) + len('-unsubscribe')
    if cgi:
        # If a list is being removed via the CGI, the best we can do is send
        # an email message to mailman-owner requesting that the appropriate
        # aliases be deleted.
        sfp = StringIO()
        print >> sfp, _("""\
The mailing list '$listname' has been removed via the through-the-web
interface.  In order to complete the de-activation of this mailing list, the
appropriate /etc/aliases (or equivalent) file must be updated.  The program
'newaliases' may also have to be run.

Here are the entries in the /etc/aliases file that should be removed:
""")
        outfp = sfp
    else:
        print _("""
To finish removing your mailing list, you must edit your /etc/aliases (or
equivalent) file by removing the following lines, and possibly running the
'newaliases' program:

## $listname mailing list""")
        outfp = sys.stdout
    # Common path
    for k, v in makealiases(mlist):
        print >> outfp, k + ':', ((fieldsz - len(k)) * ' '), v
    # If we're using the command line interface, we're done.  For ttw, we need
    # to actually send the message to mailman-owner now.
    if not cgi:
        print >> outfp
        return
    siteowner = Utils.get_site_noreply()
    # Should this be sent in the site list's preferred language?
    msg = Message.UserNotification(
        siteowner, siteowner,
        _('Mailing list removal request for list $listname'),
        sfp.getvalue(), config.DEFAULT_SERVER_LANGUAGE)
    msg['Date'] = email.Utils.formatdate(localtime=True)
    outq = Switchboard(config.OUTQUEUE_DIR)
    outq.enqueue(msg, recips=[siteowner], nodecorate=True)
