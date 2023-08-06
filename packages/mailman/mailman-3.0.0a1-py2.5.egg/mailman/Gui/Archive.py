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

from Mailman.Gui.GUIBase import GUIBase
from Mailman.configuration import config
from Mailman.i18n import _



class Archive(GUIBase):
    def GetConfigCategory(self):
        return 'archive', _('Archiving Options')

    def GetConfigInfo(self, mlist, category, subcat=None):
        if category <> 'archive':
            return None
	return [
            _("List traffic archival policies."),

	    ('archive', config.Toggle, (_('No'), _('Yes')), 0, 
	     _('Archive messages?')),

	    ('archive_private', config.Radio, (_('public'), _('private')), 0,
             _('Is archive file source for public or private archival?')),

 	    ('archive_volume_frequency', config.Radio, 
             (_('Yearly'), _('Monthly'), _('Quarterly'),
              _('Weekly'), _('Daily')),
             0,
 	     _('How often should a new archive volume be started?')),
	    ]
