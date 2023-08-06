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

"""Virgin message queue runner.

This qrunner handles messages that the Mailman system gives virgin birth to.
E.g. acknowledgement responses to user posts or Replybot messages.  They need
to go through some minimal processing before they can be sent out to the
recipient.
"""

from mailman.app.pipelines import process
from mailman.configuration import config
from mailman.queue import Runner



class VirginRunner(Runner):
    QDIR = config.VIRGINQUEUE_DIR

    def _dispose(self, mlist, msg, msgdata):
        # We need to fast track this message through any pipeline handlers
        # that touch it, e.g. especially cook-headers.
        msgdata['_fasttrack'] = True
        # Use the 'virgin' pipeline.
        process(mlist, msg, msgdata, 'virgin')
        # Do not keep this message queued.
        return False
