# Copyright (C) 2001-2009 by the Free Software Foundation, Inc.
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

"""Get the normal delivery recipients from a Sendmail style :include: file."""

__metaclass__ = type
__all__ = [
    'FileRecipients',
    ]


import os
import errno

from zope.interface import implements

from mailman.i18n import _
from mailman.interfaces import IHandler



class FileRecipients:
    """Get the normal delivery recipients from an include file."""

    implements(IHandler)

    name = 'file-recipients'
    description = _('Get the normal delivery recipients from an include file.')

    def process(self, mlist, msg, msgdata):
        """See `IHandler`."""
        if 'recips' in msgdata:
            return
        filename = os.path.join(mlist.data_path, 'members.txt')
        try:
            with open(filename) as fp:
                addrs = set(line.strip() for line in fp)
        except IOError, e:
            if e.errno <> errno.ENOENT:
                raise
            msgdata['recips'] = set()
            return
        # If the sender is a member of the list, remove them from the file
        # recipients.
        sender = msg.get_sender()
        member = mlist.members.get_member(sender)
        if member is not None:
            addrs.discard(member.address.address)
        msgdata['recips'] = addrs
