# Copyright (C) 1998-2008 by the Free Software Foundation, Inc.
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

from __future__ import with_statement

import sys

from mailman import Errors
from mailman import Message
from mailman import Utils
from mailman import i18n
from mailman.app.lifecycle import create_list
from mailman.configuration import config
from mailman.interfaces import ListAlreadyExistsError
from mailman.options import SingleMailingListOptions


_ = i18n._



class ScriptOptions(SingleMailingListOptions):
    usage=_("""\
%prog [options]

Create a new mailing list.

fqdn_listname is the 'fully qualified list name', basically the posting
address of the list.  It must be a valid email address and the domain must be
registered with Mailman.

Note that listnames are forced to lowercase.""")

    def add_options(self):
        super(ScriptOptions, self).add_options()
        self.parser.add_option(
            '--language',
            type='unicode', action='store',
            help=_("""\
Make the list's preferred language LANGUAGE, which must be a two letter
language code."""))
        self.parser.add_option(
            '-o', '--owner',
            type='unicode', action='append', default=[],
            dest='owners', help=_("""\
Specific a listowner email address.  If the address is not currently
registered with Mailman, the address is registered and linked to a user.
Mailman will send a confirmation message to the address, but it will also send
a list creation notice to the address.  More than one owner can be
specified."""))
        self.parser.add_option(
            '-q', '--quiet',
            default=False, action='store_true',
            help=_("""\
Normally the administrator is notified by email (after a prompt) that their
list has been created.  This option suppresses the prompt and
notification."""))
        self.parser.add_option(
            '-a', '--automate',
            default=False, action='store_true',
            help=_("""\
This option suppresses the prompt prior to administrator notification but
still sends the notification.  It can be used to make newlist totally
non-interactive but still send the notification, assuming at least one list
owner is specified with the -o option.."""))

    def sanity_check(self):
        """Set up some defaults we couldn't set up earlier."""
        if self.options.language is None:
            self.options.language = config.DEFAULT_SERVER_LANGUAGE
        # Is the language known?
        if self.options.language not in config.languages.enabled_codes:
            self.parser.error(_('Unknown language: $opts.language'))
        # Handle variable number of positional arguments
        if len(self.arguments) > 0:
            parser.error(_('Unexpected arguments'))



def main():
    options = ScriptOptions()
    options.initialize()

    # Create the mailing list, applying styles as appropriate.
    fqdn_listname = options.options.listname
    try:
        mlist = create_list(fqdn_listname, options.options.owners)
        mlist.preferred_language = options.options.language
    except Errors.InvalidEmailAddress:
        options.parser.error(_('Illegal list name: $fqdn_listname'))
    except ListAlreadyExistsError:
        options.parser.error(_('List already exists: $fqdn_listname'))
    except Errors.BadDomainSpecificationError, domain:
        options.parser.error(_('Undefined domain: $domain'))

    config.db.commit()

    # Send notices to the list owners.  XXX This should also be moved to the
    # Mailman.app.create module.
    if not options.options.quiet and not options.options.automate:
        print _('Hit enter to notify $fqdn_listname owners...'),
        sys.stdin.readline()
    if not options.options.quiet:
        d = dict(
            listname        = mlist.fqdn_listname,
            admin_url       = mlist.script_url('admin'),
            listinfo_url    = mlist.script_url('listinfo'),
            requestaddr     = mlist.request_address,
            siteowner       = mlist.no_reply_address,
            )
        text = Utils.maketext('newlist.txt', d, mlist=mlist)
        # Set the I18N language to the list's preferred language so the header
        # will match the template language.  Stashing and restoring the old
        # translation context is just (healthy? :) paranoia.
        with i18n.using_language(mlist.preferred_language):
            msg = Message.UserNotification(
                owner_mail, mlist.no_reply_address,
                _('Your new mailing list: $fqdn_listname'),
                text, mlist.preferred_language)
            msg.send(mlist)
