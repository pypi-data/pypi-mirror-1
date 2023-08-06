# Copyright (C) 2000-2008 by the Free Software Foundation, Inc.
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

import os
import sys
import time
import string
import gettext

import mailman.messages
from mailman.SafeDict import SafeDict
from mailman.configuration import config

_translation = None
_missing = object()

MESSAGES_DIR = os.path.dirname(mailman.messages.__file__)



class Template(string.Template):
    idpattern = r'[_a-z][_a-z0-9.]*'


class attrdict(dict):
    def __getitem__(self, key):
        parts = key.split('.')
        value = super(attrdict, self).__getitem__(parts.pop(0))
        while parts:
            value = getattr(value, parts.pop(0), _missing)
            if value is _missing:
                raise KeyError(key)
        return value



def set_language(language=None):
    global _translation
    if language is not None:
        language = [language]
    try:
        _translation = gettext.translation('mailman', MESSAGES_DIR, language)
    except IOError:
        # The selected language was not installed in messages, so fall back to
        # untranslated English.
        _translation = gettext.NullTranslations()


def get_translation():
    return _translation


def set_translation(translation):
    global _translation
    _translation = translation


class using_language(object):
    """Context manager for Python 2.5's `with` statement."""
    def __init__(self, language):
        self._language = language
        self._old_translation = None

    def __enter__(self):
        self._old_translation = _translation
        set_language(self._language)

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _translation
        _translation = self._old_translation


# Set up the global translation based on environment variables.  Mostly used
# for command line scripts.
if _translation is None:
    _translation = gettext.NullTranslations()



def _(s):
    if s == '':
        return u''
    assert s, 'Cannot translate: %s' % s
    # Do translation of the given string into the current language, and do PEP
    # 292 style $-string interpolation into the resulting string.
    #
    # This lets you write something like:
    #
    #     now = time.ctime(time.time())
    #     print _('The current time is: $now')
    #
    # and have it Just Work.  Note that the lookup order for keys in the
    # original string is 1) locals dictionary, 2) globals dictionary.
    #
    # Get the frame of the caller.
    frame = sys._getframe(1)
    # A `safe' dictionary is used so we won't get an exception if there's a
    # missing key in the dictionary.
    d = frame.f_globals.copy()
    d.update(frame.f_locals)
    # Mailman must be unicode safe internally (i.e. all strings inside Mailman
    # must be unicodes).  The translation service is one boundary to the
    # outside world, so to honor this constraint, make sure that all strings
    # to come out of _() are unicodes, even if the translated string or
    # dictionary values are 8-bit strings.
    tns = _translation.ugettext(s)
    charset = _translation.charset() or 'us-ascii'
    for k, v in d.items():
        if isinstance(v, str):
            d[k] = unicode(v, charset, 'replace')
    translated_string = Template(tns).safe_substitute(attrdict(d))
    if isinstance(translated_string, str):
        translated_string = unicode(translated_string, charset)
    return translated_string



def ctime(date):
    # Don't make these module globals since we have to do runtime translation
    # of the strings anyway.
    daysofweek = [
        _('Mon'), _('Tue'), _('Wed'), _('Thu'),
        _('Fri'), _('Sat'), _('Sun')
        ]
    months = [
        '',
        _('Jan'), _('Feb'), _('Mar'), _('Apr'), _('May'), _('Jun'),
        _('Jul'), _('Aug'), _('Sep'), _('Oct'), _('Nov'), _('Dec')
        ]

    tzname = _('Server Local Time')
    if isinstance(date, str):
        try:
            year, mon, day, hh, mm, ss, wday, ydat, dst = time.strptime(date)
            if dst in (0,1):
                tzname = time.tzname[dst]
            else:
                # MAS: No exception but dst = -1 so try
                return ctime(time.mktime((year, mon, day, hh, mm, ss, wday,
                                          ydat, dst)))
        except (ValueError, AttributeError):
            try:
                wday, mon, day, hms, year = date.split()
                hh, mm, ss = hms.split(':')
                year = int(year)
                day = int(day)
                hh = int(hh)
                mm = int(mm)
                ss = int(ss)
            except ValueError:
                return date
            else:
                for i in range(0, 7):
                    wconst = (1999, 1, 1, 0, 0, 0, i, 1, 0)
                    if wday.lower() == time.strftime('%a', wconst).lower():
                        wday = i
                        break
                for i in range(1, 13):
                    mconst = (1999, i, 1, 0, 0, 0, 0, 1, 0)
                    if mon.lower() == time.strftime('%b', mconst).lower():
                        mon = i
                        break
    else:
        year, mon, day, hh, mm, ss, wday, yday, dst = time.localtime(date)
        if dst in (0, 1):
            tzname = time.tzname[dst]

    wday = daysofweek[wday]
    mon = months[mon]
    return _('%(wday)s %(mon)s %(day)2i %(hh)02i:%(mm)02i:%(ss)02i '
             '%(tzname)s %(year)04i')
