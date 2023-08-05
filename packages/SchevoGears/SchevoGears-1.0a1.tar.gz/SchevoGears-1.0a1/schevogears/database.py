"""Schevo-specific addins for TurboGears.

XXX: The locking mechanisms employed here are not thoroughly tested in
the face of failure.  Use carefully for now!

For copyright, license, and warranty, see bottom of file.
"""

import pkg_resources
pkg_resources.require("TurboGears")

import schevo.database
import schevo.mt

import turbogears

open_schevo_databases = {}


def package_database(package_name=None):
    """A Schevo database wrapper that looks for the filename based on a
    package name, or is None if no filename was found."""
    if package_name in open_schevo_databases:
        return open_schevo_databases[package_name]
    filename = None
    if package_name:
        filename = turbogears.config.get(
            '%s.schevo.dbfile' % package_name, None)
    if not filename:
        filename = turbogears.config.get('schevo.dbfile', None)
    if filename:
        # Open the database.
        db = schevo.database.open(filename)
        # Install the multi-threading plugin.
        schevo.mt.install(db)
        open_schevo_databases[package_name] = db
        return db
    # No database was found.
    return None


# Auto-reload in CherryPy poses some problems, so make sure opened databases
# are closed when auto-reloading.
from cherrypy.lib import autoreload
_restart_with_reloader = autoreload.restart_with_reloader
def restart_with_reloader():
    global open_schevo_databases
    for db in open_schevo_databases.values():
        db.close()
    open_schevo_databases = {}
    return _restart_with_reloader()
autoreload.restart_with_reloader = restart_with_reloader


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
