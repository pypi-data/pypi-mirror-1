"""Schevo+TurboGears jsonify support.

For copyright, license, and warranty, see bottom of file.
"""

from turbojson import jsonify as tj

from schevo.base import Entity, Extent


# Namespace convenience.
jsonify = tj.jsonify


@jsonify.when('isinstance(obj, Entity)')
def jsonify_schevo(obj):
    result = {}
    result['_oid'] = obj.sys.oid
    result['_rev'] = obj.sys.rev
    for name, value in obj.sys.fields().value_map().iteritems():
        result[name] = jsonify(value)
    return result


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
