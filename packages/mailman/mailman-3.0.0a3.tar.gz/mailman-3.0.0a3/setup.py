# Copyright (C) 2007-2009 by the Free Software Foundation, Inc.
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

import ez_setup
ez_setup.use_setuptools()

import sys
from string import Template

sys.path.insert(0, 'src')

from mailman.version import VERSION as __version__
from setuptools import setup, find_packages



if sys.hexversion < 0x20600f0:
    print 'Mailman requires at least Python 2.6'
    sys.exit(1)



# Ensure that all the .mo files are generated from the corresponding .po file.
# This procedure needs to be made sane, probably when the language packs are
# properly split out.

import os
import mailman.commands
import mailman.messages

start_dir = os.path.dirname(mailman.messages.__file__)
for dirpath, dirnames, filenames in os.walk(start_dir):
    for filename in filenames:
        po_file = os.path.join(dirpath, filename)
        basename, ext = os.path.splitext(po_file)
        if ext <> '.po':
            continue
        mo_file = basename + '.mo'
        if (not os.path.exists(mo_file) or
            os.path.getmtime(po_file) > os.path.getmtime(mo_file)):
            # The mo file doesn't exist or is older than the po file.
            os.system('msgfmt -o %s %s' % (mo_file, po_file))



# XXX The 'bin/' prefix here should be configurable.
template = Template('$script = mailman.bin.$script:main')
scripts = set(
    template.substitute(script=script)
    for script in ('mailman', 'mailmanctl', 'qrunner', 'master')
    )



setup(
    name            = 'mailman',
    version         = __version__,
    description     = 'Mailman -- the GNU mailing list manager',
    long_description= """\
This is GNU Mailman, a mailing list management system distributed under the
terms of the GNU General Public License (GPL) version 3 or later.  The name of
this software is spelled 'Mailman' with a leading capital 'M' but with a lower
case second `m'.  Any other spelling is incorrect.""",
    author          = 'The Mailman Developers',
    author_email    = 'mailman-developers@python.org',
    license         = 'GPLv3',
    url             = 'http://www.list.org',
    keywords        = 'email',
    packages        = find_packages('src'),
    package_dir     = {'': 'src'},
    include_package_data = True,
    entry_points    = {
        'console_scripts' : list(scripts),
        },
    install_requires = [
        'argparse',
        'lazr.config',
        'lazr.delegates',
        'lazr.restful',
        'locknix',
        'munepy',
        'storm',
        'zope.schema',
        'zope.interface',
        ],
    setup_requires = [
        'setuptools_bzr',
        ],
    extras_require=dict(
        docs=['Sphinx', 'z3c.recipe.sphinxdoc'],
        )
    )
