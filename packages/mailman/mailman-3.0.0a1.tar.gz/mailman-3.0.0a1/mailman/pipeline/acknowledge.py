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

"""Send an acknowledgment of the successful post to the sender.

This only happens if the sender has set their AcknowledgePosts attribute.
"""

__metaclass__ = type
__all__ = ['Acknowledge']


from zope.interface import implements

from mailman import Errors
from mailman import Message
from mailman import Utils
from mailman.configuration import config
from mailman.i18n import _
from mailman.interfaces import IHandler



class Acknowledge:
    """Send an acknowledgment."""
    implements(IHandler)

    name = 'acknowledge'
    description = _("""Send an acknowledgment of a posting.""")

    def process(self, mlist, msg, msgdata):
        """See `IHandler`."""
        # Extract the sender's address and find them in the user database
        sender = msgdata.get('original_sender', msg.get_sender())
        member = mlist.members.get_member(sender)
        if member is None or not member.acknowledge_posts:
            # Either the sender is not a member, in which case we can't know
            # whether they want an acknowlegment or not, or they are a member
            # who definitely does not want an acknowlegment.
            return
        # Okay, they are a member that wants an acknowledgment of their post.
        # Give them their original subject.  BAW: do we want to use the
        # decoded header?
        original_subject = msgdata.get(
            'origsubj', msg.get('subject', _('(no subject)')))
        # Get the user's preferred language.
        lang = msgdata.get('lang', member.preferred_language)
        # Now get the acknowledgement template.
        realname = mlist.real_name
        text = Utils.maketext(
            'postack.txt',
            {'subject'     : Utils.oneline(original_subject,
                                           Utils.GetCharSet(lang)),
             'listname'    : realname,
             'listinfo_url': mlist.script_url('listinfo'),
             'optionsurl'  : member.options_url,
             }, lang=lang, mlist=mlist, raw=True)
        # Craft the outgoing message, with all headers and attributes
        # necessary for general delivery.  Then enqueue it to the outgoing
        # queue.
        subject = _('$realname post acknowledgment')
        usermsg = Message.UserNotification(sender, mlist.bounces_address,
                                           subject, text, lang)
        usermsg.send(mlist)
