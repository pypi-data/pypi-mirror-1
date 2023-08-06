# Copyright (C) 1998-2009 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <http://www.gnu.org/licenses/>.

"""-request robot command queue runner."""

__metaclass__ = type
__all__ = [
    'CommandRunner',
    'Results',
    ]

# See the delivery diagram in IncomingRunner.py.  This module handles all
# email destined for mylist-request, -join, and -leave.  It no longer handles
# bounce messages (i.e. -admin or -bounces), nor does it handle mail to
# -owner.

import re
import sys
import logging

from StringIO import StringIO
from email.Errors import HeaderParseError
from email.Header import decode_header, make_header, Header
from email.Iterators import typed_subpart_iterator
from email.MIMEMessage import MIMEMessage
from email.MIMEText import MIMEText
from zope.interface import implements

from mailman import Defaults
from mailman import Message
from mailman import Utils
from mailman.app.replybot import autorespond_to_sender
from mailman.config import config
from mailman.i18n import _
from mailman.interfaces import ContinueProcessing, IEmailResults
from mailman.queue import Runner

NL = '\n'

log = logging.getLogger('mailman.vette')



class CommandFinder:
    """Generate commands from the content of a message."""

    def __init__(self, msg, msgdata, results):
        self.command_lines = []
        self.ignored_lines = []
        self.processed_lines = []
        # Depending on where the message was destined to, add some implicit
        # commands.  For example, if this was sent to the -join or -leave
        # addresses, it's the same as if 'join' or 'leave' commands were sent
        # to the -request address.
        if msgdata.get('tojoin'):
            self.command_lines.append('join')
        elif msgdata.get('toleave'):
            self.command_lines.append('leave')
        elif msgdata.get('toconfirm'):
            mo = re.match(Defaults.VERP_CONFIRM_REGEXP, msg.get('to', ''))
            if mo:
                self.command_lines.append('confirm ' + mo.group('cookie'))
        # Extract the subject header and do RFC 2047 decoding.
        raw_subject = msg.get('subject', '')
        try:
            subject = unicode(make_header(decode_header(raw_subject)))
            # Mail commands must be ASCII.
            self.command_lines.append(subject.encode('us-ascii'))
        except (HeaderParseError, UnicodeError, LookupError):
            # The Subject header was unparseable or not ASCII, so just ignore
            # it.
            pass
        # Find the first text/plain part of the message.
        part = None
        for part in typed_subpart_iterator(msg, 'text', 'plain'):
            break
        if part is None or part is not msg:
            # Either there was no text/plain part or we ignored some
            # non-text/plain parts.
            print >> results, _('Ignoring non-text/plain MIME parts')
        if part is None:
            # There was no text/plain part to be found.
            return
        body = part.get_payload(decode=True)
        # text/plain parts better have string payloads.
        assert isinstance(body, basestring), 'Non-string decoded payload'
        lines = body.splitlines()
        # Use no more lines than specified
        self.command_lines.extend(lines[:Defaults.EMAIL_COMMANDS_MAX_LINES])
        self.ignored_lines.extend(lines[Defaults.EMAIL_COMMANDS_MAX_LINES:])

    def __iter__(self):
        """Return each command line, split into commands and arguments.

        :return: 2-tuples where the first element is the command and the
            second element is a tuple of the arguments.
        """
        while self.command_lines:
            line = self.command_lines.pop(0)
            self.processed_lines.append(line)
            parts = line.strip().split()
            if len(parts) == 0:
                continue
            command = parts.pop(0)
            yield command, tuple(parts)



class Results:
    """The email command results."""

    implements(IEmailResults)

    def __init__(self):
        self._output = StringIO()
        print >> self._output, _("""\
The results of your email command are provided below.
""")

    def write(self, text):
        self._output.write(text)

    def __unicode__(self):
        value = self._output.getvalue()
        assert isinstance(value, unicode), 'Not a unicode: %r' % value
        return value



class CommandRunner(Runner):
    """The email command runner."""

    def _dispose(self, mlist, msg, msgdata):
        message_id = msg.get('message-id', 'n/a')
        # The policy here is similar to the Replybot policy.  If a message has
        # "Precedence: bulk|junk|list" and no "X-Ack: yes" header, we discard
        # the command message.
        precedence = msg.get('precedence', '').lower()
        ack = msg.get('x-ack', '').lower()
        if ack <> 'yes' and precedence in ('bulk', 'junk', 'list'):
            log.info('%s Precedence: %s message discarded by: %s',
                     message_id, precedence, mlist.request_address)
            return False
        # Do replybot for commands.
        replybot = config.handlers['replybot']
        replybot.process(mlist, msg, msgdata)
        if mlist.autorespond_requests == 1:
            # Respond and discard.
            log.info('%s -request message replied and discard', message_id)
            return False
        # Now craft the response and process the command lines.
        results = Results()
        # Include just a few key pieces of information from the original: the
        # sender, date, and message id.
        print >> results, _('- Original message details:')
        subject = msg.get('subject', 'n/a')
        date = msg.get('date', 'n/a')
        from_ = msg.get('from', 'n/a')
        print >> results, _('    From: $from_')
        print >> results, _('    Subject: $subject')
        print >> results, _('    Date: $date')
        print >> results, _('    Message-ID: $message_id')
        print >> results, _('\n- Results:')
        finder = CommandFinder(msg, msgdata, results)
        for command_name, arguments in finder:
            command = config.commands.get(command_name)
            if command is None:
                print >> results, _('No such command: $command_name')
            else:
                status = command.process(
                    mlist, msg, msgdata, arguments, results)
                assert status in ContinueProcessing, (
                    'Invalid status: %s' % status)
                if status == ContinueProcessing.no:
                    break
        # All done, send the response.
        if len(finder.command_lines) > 0:
            print >> results, _('\n- Unprocessed:')
            for line in finder.command_lines:
                print >> results, line
        if len(finder.ignored_lines) > 0:
            print >> results, _('\n- Ignored:')
            for line in finder.ignored_lines:
                print >> results, line
        print >> results, _('\n- Done.')
        # Send a reply, but do not attach the original message.  This is a
        # compromise because the original message is often helpful in tracking
        # down problems, but it's also a vector for backscatter spam.
        reply = Message.UserNotification(
            msg.get_sender(), mlist.bounces_address,
            _('The results of your email commands'),
            lang=msgdata['lang'])
        # Find a charset for the response body.  Try ascii first, then
        # latin-1 and finally falling back to utf-8.
        reply_body = unicode(results)
        for charset in ('us-ascii', 'latin-1'):
            try:
                reply_body.encode(charset)
                break
            except UnicodeError:
                pass
        else:
            charset = 'utf-8'
        reply.set_payload(reply_body, charset=charset)
        reply.send(mlist)
