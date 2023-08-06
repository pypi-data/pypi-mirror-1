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

"""Process subscription or roster requests from listinfo form."""

from __future__ import with_statement

import os
import cgi
import sys
import logging

from Mailman import Errors
from Mailman import MailList
from Mailman import Message
from Mailman import Utils
from Mailman import i18n
from Mailman.UserDesc import UserDesc
from Mailman.configuration import config
from Mailman.htmlformat import *

SLASH = '/'
ERRORSEP = '\n\n<p>'

# Set up i18n
_ = i18n._
i18n.set_language(config.DEFAULT_SERVER_LANGUAGE)

log     = logging.getLogger('mailman.error')
mlog    = logging.getLogger('mailman.mischief')



def main():
    doc = Document()
    doc.set_language(config.DEFAULT_SERVER_LANGUAGE)

    parts = Utils.GetPathPieces()
    if not parts:
        doc.AddItem(Header(2, _("Error")))
        doc.AddItem(Bold(_('Invalid options to CGI script')))
        print doc.Format()
        return

    listname = parts[0].lower()
    try:
        mlist = MailList.MailList(listname, lock=0)
    except Errors.MMListError, e:
        # Avoid cross-site scripting attacks
        safelistname = Utils.websafe(listname)
        doc.AddItem(Header(2, _("Error")))
        doc.AddItem(Bold(_('No such list <em>%(safelistname)s</em>')))
        print doc.Format()
        log.error('No such list "%s": %s\n', listname, e)
        return

    # See if the form data has a preferred language set, in which case, use it
    # for the results.  If not, use the list's preferred language.
    cgidata = cgi.FieldStorage()
    language = cgidata.getvalue('language')
    if language not in config.languages.enabled_codes:
        language = mlist.preferred_language
    i18n.set_language(language)
    doc.set_language(language)

    mlist.Lock()
    try:
        process_form(mlist, doc, cgidata, language)
        mlist.Save()
    finally:
        mlist.Unlock()



def process_form(mlist, doc, cgidata, lang):
    listowner = mlist.GetOwnerEmail()
    realname = mlist.real_name
    results = []

    # The email address being subscribed, required
    email = cgidata.getvalue('email', '')
    if not email:
        results.append(_('You must supply a valid email address.'))

    fullname = cgidata.getvalue('fullname', '')
    # Canonicalize the full name
    fullname = Utils.canonstr(fullname, lang)
    # Who was doing the subscribing?
    remote = os.environ.get('REMOTE_HOST',
                            os.environ.get('REMOTE_ADDR',
                                           'unidentified origin'))
    # Was an attempt made to subscribe the list to itself?
    if email == mlist.GetListEmail():
        mlog.error('Attempt to self subscribe %s: %s', email, remote)
        results.append(_('You may not subscribe a list to itself!'))
    # If the user did not supply a password, generate one for him
    password = cgidata.getvalue('pw')
    confirmed = cgidata.getvalue('pw-conf')

    if password is None and confirmed is None:
        password = Utils.MakeRandomPassword()
    elif password is None or confirmed is None:
        results.append(_('If you supply a password, you must confirm it.'))
    elif password <> confirmed:
        results.append(_('Your passwords did not match.'))

    # Get the digest option for the subscription.
    digestflag = cgidata.getvalue('digest')
    if digestflag:
        try:
            digest = int(digestflag)
        except ValueError:
            digest = 0
    else:
        digest = mlist.digest_is_default

    # Sanity check based on list configuration.  BAW: It's actually bogus that
    # the page allows you to set the digest flag if you don't really get the
    # choice. :/
    if not mlist.digestable:
        digest = 0
    elif not mlist.nondigestable:
        digest = 1

    if results:
        print_results(mlist, ERRORSEP.join(results), doc, lang)
        return

    # If this list has private rosters, we have to be careful about the
    # message that gets printed, otherwise the subscription process can be
    # used to mine for list members.  It may be inefficient, but it's still
    # possible, and that kind of defeats the purpose of private rosters.
    # We'll use this string for all successful or unsuccessful subscription
    # results.
    if mlist.private_roster == 0:
        # Public rosters
        privacy_results = ''
    else:
        privacy_results = _("""\
Your subscription request has been received, and will soon be acted upon.
Depending on the configuration of this mailing list, your subscription request
may have to be first confirmed by you via email, or approved by the list
moderator.  If confirmation is required, you will soon get a confirmation
email which contains further instructions.""")

    try:
        userdesc = UserDesc(email, fullname, password, digest, lang)
        mlist.AddMember(userdesc, remote)
        results = ''
    # Check for all the errors that mlist.AddMember can throw options on the
    # web page for this cgi
    except Errors.MembershipIsBanned:
        results = _("""The email address you supplied is banned from this
        mailing list.  If you think this restriction is erroneous, please
        contact the list owners at %(listowner)s.""")
    except Errors.InvalidEmailAddress:
        results = _('The email address you supplied is not valid.')
    except Errors.MMSubscribeNeedsConfirmation:
        # Results string depends on whether we have private rosters or not
        if privacy_results:
            results = privacy_results
        else:
            results = _("""\
Confirmation from your email address is required, to prevent anyone from
subscribing you without permission.  Instructions are being sent to you at
%(email)s.  Please note your subscription will not start until you confirm
your subscription.""")
    except Errors.MMNeedApproval, x:
        # Results string depends on whether we have private rosters or not
        if privacy_results:
            results = privacy_results
        else:
            # We need to interpolate into x
            x = _(x)
            results = _("""\
Your subscription request was deferred because %(x)s.  Your request has been
forwarded to the list moderator.  You will receive email informing you of the
moderator's decision when they get to your request.""")
    except Errors.MMAlreadyAMember:
        # Results string depends on whether we have private rosters or not
        if not privacy_results:
            results = _('You are already subscribed.')
        else:
            results = privacy_results
            # This could be a membership probe.  For safety, let the user know
            # a probe occurred.  BAW: should we inform the list moderator?
            listaddr = mlist.GetListEmail()
            # Set the language for this email message to the member's language.
            mlang = mlist.getMemberLanguage(email)
            with i18n.using_language(mlang):
                msg = Message.UserNotification(
                    mlist.getMemberCPAddress(email),
                    mlist.GetBouncesEmail(),
                    _('Mailman privacy alert'),
                    _("""\
An attempt was made to subscribe your address to the mailing list
%(listaddr)s.  You are already subscribed to this mailing list.

Note that the list membership is not public, so it is possible that a bad
person was trying to probe the list for its membership.  This would be a
privacy violation if we let them do this, but we didn't.

If you submitted the subscription request and forgot that you were already
subscribed to the list, then you can ignore this message.  If you suspect that
an attempt is being made to covertly discover whether you are a member of this
list, and you are worried about your privacy, then feel free to send a message
to the list administrator at %(listowner)s.
"""), lang=mlang)
            msg.send(mlist)
    # These shouldn't happen unless someone's tampering with the form
    except Errors.MMCantDigestError:
        results = _('This list does not support digest delivery.')
    except Errors.MMMustDigestError:
        results = _('This list only supports digest delivery.')
    else:
        # Everything's cool.  Our return string actually depends on whether
        # this list has private rosters or not
        if privacy_results:
            results = privacy_results
        else:
            results = _("""\
You have been successfully subscribed to the %(realname)s mailing list.""")
    # Show the results
    print_results(mlist, results, doc, lang)



def print_results(mlist, results, doc, lang):
    # The bulk of the document will come from the options.html template, which
    # includes its own html armor (head tags, etc.).  Suppress the head that
    # Document() derived pages get automatically.
    doc.suppress_head = 1

    replacements = mlist.GetStandardReplacements(lang)
    replacements['<mm-results>'] = results
    output = mlist.ParseTags('subscribe.html', replacements, lang)
    doc.AddItem(output)
    print doc.Format()
