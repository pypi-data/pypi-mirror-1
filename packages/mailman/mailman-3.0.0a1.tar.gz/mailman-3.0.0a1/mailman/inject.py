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

__metaclass__ = type
__all__ = [
    'inject_message',
    'inject_text',
    ]


from email import message_from_string
from email.utils import formatdate, make_msgid

from mailman.Message import Message
from mailman.configuration import config
from mailman.queue import Switchboard



def inject_message(mlist, msg, recips=None, qdir=None):
    """Inject a message into a queue.

    :param mlist: The mailing list this message is destined for.
    :param msg: The Message object to inject.
    :param recips: Optional set of recipients to put into the message's
        metadata.
    :param qdir: Optional queue directory to inject this message into.  If not
        given, the incoming queue is used.
    """
    if qdir is None:
        qdir = config.INQUEUE_DIR
    # Since we're crafting the message from whole cloth, let's make sure this
    # message has a Message-ID.
    if 'message-id' not in msg:
        msg['Message-ID'] = make_msgid()
    # Ditto for Date: as required by RFC 2822.
    if 'date' not in msg:
        msg['Date'] = formatdate(localtime=True)
    queue = Switchboard(qdir)
    kws = dict(
        listname=mlist.fqdn_listname,
        tolist=True,
        original_size=getattr(msg, 'original_size', len(msg.as_string())),
        )
    if recips is not None:
        kws['recips'] = recips
    queue.enqueue(msg, **kws)



def inject_text(mlist, text, recips=None, qdir=None):
    """Inject a message into a queue.

    :param mlist: The mailing list this message is destined for.
    :param text: The text of the message to inject.  This will be parsed into
        a Message object.
    :param recips: Optional set of recipients to put into the message's
        metadata.
    :param qdir: Optional queue directory to inject this message into.  If not
        given, the incoming queue is used.
    """
    message = message_from_string(text, Message)
    message.original_size = len(text)
    inject_message(mlist, message, recips, qdir)
