# Copyright (C) 2007-2008 by the Free Software Foundation, Inc.
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

from storm.locals import *
from zope.interface import implements

from mailman.Utils import split_listname
from mailman.configuration import config
from mailman.constants import SystemDefaultPreferences
from mailman.database.model import Model
from mailman.database.types import Enum
from mailman.interfaces import IMember, IPreferences



class Member(Model):
    implements(IMember)

    id = Int(primary=True)
    role = Enum()
    mailing_list = Unicode()
    is_moderated = Bool()

    address_id = Int()
    address = Reference(address_id, 'Address.id')
    preferences_id = Int()
    preferences = Reference(preferences_id, 'Preferences.id')

    def __init__(self, role, mailing_list, address):
        self.role = role
        self.mailing_list = mailing_list
        self.address = address
        self.is_moderated = False

    def __repr__(self):
        return '<Member: %s on %s as %s>' % (
            self.address, self.mailing_list, self.role)

    def _lookup(self, preference):
        pref = getattr(self.preferences, preference)
        if pref is not None:
            return pref
        pref = getattr(self.address.preferences, preference)
        if pref is not None:
            return pref
        if self.address.user:
            pref = getattr(self.address.user.preferences, preference)
            if pref is not None:
                return pref
        return getattr(SystemDefaultPreferences, preference)

    @property
    def acknowledge_posts(self):
        return self._lookup('acknowledge_posts')

    @property
    def preferred_language(self):
        return self._lookup('preferred_language')

    @property
    def receive_list_copy(self):
        return self._lookup('receive_list_copy')

    @property
    def receive_own_postings(self):
        return self._lookup('receive_own_postings')

    @property
    def delivery_mode(self):
        return self._lookup('delivery_mode')

    @property
    def delivery_status(self):
        return self._lookup('delivery_status')

    @property
    def options_url(self):
        # XXX Um, this is definitely wrong
        return 'http://example.com/' + self.address.address

    def unsubscribe(self):
        config.db.store.remove(self.preferences)
        config.db.store.remove(self)
