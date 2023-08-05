"""Schevo extensions for TurboGears.

For copyright, license, and warranty, see bottom of file.
"""

import sys

from paste.script import templates

import turbogears
from turbogears.command import quickstart as tgquickstart
from turbogears import visit as tgvisit

from schevogears import visit as sgvisit


original = tgquickstart.quickstart
class quickstart(original):

    desc = 'Create a new Schevo/TurboGears project'

    def __init__(self, version):
        original.__init__(self, version)
        if self.templates:
            self.templates += ' schevo schevogears'
        else:
            self.templates = 'schevo schevogears'


def install():
    print 'Installing Schevo extensions for TurboGears.'
    # Create new quickstart command.
    tgquickstart.quickstart = quickstart
    # Monkey-patch turbogears.visit to side-step SQLObject use.
    tgvisit.start_extension = sgvisit.start_extension
    tgvisit.shutdown_extension = tgvisit.shutdown_extension


def tg_admin(argv):
    sys.argv = argv
    import turbogears.command
    return turbogears.command.main()


# Copyright (C) 2001-2005 Orbtech, L.L.C.
#
# Schevo
# http://schevo.org/
#
# Orbtech
# Saint Louis, MO
# http://orbtech.com/
#
# This toolkit is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This toolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
