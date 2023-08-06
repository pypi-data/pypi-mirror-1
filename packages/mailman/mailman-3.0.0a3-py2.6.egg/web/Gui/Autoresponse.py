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

"""Administrative GUI for the autoresponder."""

from Mailman import Utils
from Mailman.Gui.GUIBase import GUIBase
from Mailman.configuration import config
from Mailman.i18n import _

# These are the allowable string substitution variables
ALLOWEDS = ('listname', 'listurl', 'requestemail', 'adminemail', 'owneremail')



class Autoresponse(GUIBase):
    def GetConfigCategory(self):
        return 'autoreply', _('Auto-responder')

    def GetConfigInfo(self, mlist, category, subcat=None):
        if category <> 'autoreply':
            return None
        WIDTH = config.TEXTFIELDWIDTH

        return [
            _("""\
Auto-responder characteristics.<p>

In the text fields below, string interpolation is performed with
the following key/value substitutions:
<p><ul>
    <li><b>listname</b> - <em>gets the name of the mailing list</em>
    <li><b>listurl</b> - <em>gets the list's listinfo URL</em>
    <li><b>requestemail</b> - <em>gets the list's -request address</em>
    <li><b>owneremail</b> - <em>gets the list's -owner address</em>
</ul>

<p>For each text field, you can either enter the text directly into the text
box, or you can specify a file on your local system to upload as the text."""),

            ('autorespond_postings', config.Toggle, (_('No'), _('Yes')), 0,
             _('''Should Mailman send an auto-response to mailing list
             posters?''')),

            ('autoresponse_postings_text', config.FileUpload,
             (6, WIDTH), 0,
             _('Auto-response text to send to mailing list posters.')),

            ('autorespond_admin', config.Toggle, (_('No'), _('Yes')), 0,
             _('''Should Mailman send an auto-response to emails sent to the
             -owner address?''')),

            ('autoresponse_admin_text', config.FileUpload,
             (6, WIDTH), 0,
             _('Auto-response text to send to -owner emails.')),

            ('autorespond_requests', config.Radio,
             (_('No'), _('Yes, w/discard'), _('Yes, w/forward')), 0,
             _('''Should Mailman send an auto-response to emails sent to the
             -request address?  If you choose yes, decide whether you want
             Mailman to discard the original email, or forward it on to the
             system as a normal mail command.''')),

            ('autoresponse_request_text', config.FileUpload,
             (6, WIDTH), 0,
             _('Auto-response text to send to -request emails.')),

            ('autoresponse_graceperiod', config.Number, 3, 0,
             _('''Number of days between auto-responses to either the mailing
             list or -request/-owner address from the same poster.  Set to
             zero (or negative) for no grace period (i.e. auto-respond to
             every message).''')),
            ]

    def _setValue(self, mlist, property, val, doc):
        # Handle these specially because we may need to convert to/from
        # external $-string representation.
        if property in ('autoresponse_postings_text',
                        'autoresponse_admin_text',
                        'autoresponse_request_text'):
            val = self._convertString(mlist, property, ALLOWEDS, val, doc)
            if val is None:
                # There was a problem, so don't set it
                return
        GUIBase._setValue(self, mlist, property, val, doc)
