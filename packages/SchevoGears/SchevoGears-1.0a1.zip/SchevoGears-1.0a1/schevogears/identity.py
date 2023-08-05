"""schevogears identity support.

For copyright, license, and warranty, see bottom of file.
"""

import cherrypy
from turbogears import identity

from schevo import error

from schevogears.database import package_database

import logging
log = logging.getLogger('turbogears.identity')


## db = package_database("turbogears.identity")
db = package_database()


class SchevoIdentity(object):

    def __init__(self, visit_id, user=None):
        self._user = user
        self.visit_id = visit_id

    @property
    def user(self):
        if self._user is not None:
            return self._user
        lock = db.read_lock()
        try:
            if self.visit_id in db.IdentityVisit:
                visit = db.IdentityVisit[self.visit_id]
                visit_user = db.IdentityVisitUser.findone(visit=visit)
                if visit_user is not None:
                    self._user = visit_user.user
                    return self._user
            else:
                # Visit ID is invalid.
                self._user = None
                return None
        finally:
            lock.release()

    @property
    def user_name(self):
        user = self.user
        if user is None:
            return None
        else:
            lock = db.read_lock()
            try:
                return self.user.name
            finally:
                lock.release()

    @property
    def anonymous(self):
        return self.user is None

    @property
    def permissions(self):
        try:
            return self._permissions
        except AttributeError:
            pass
        user = self.user
        if user is None:
            self._permissions = frozenset()
        else:
            lock = db.read_lock()
            try:
                self._permissions = frozenset(
                    perm.name for perm in user.x.permissions())
            finally:
                lock.release()
        return self._permissions

    @property
    def groups(self):
        try:
            return self._groups
        except AttributeError:
            pass
        user = self.user
        if user is None:
            self._groups = frozenset()
        else:
            lock = db.read_lock()
            try:
                self._groups = frozenset(
                    group.name for group in user.x.groups())
            finally:
                lock.release()
        return self._groups

    def logout(self):
        """Remove link between this identity and the visit."""
        if not self.visit_id:
            return
        lock = db.write_lock()
        try:
            if self.visit_id in db.IdentityVisit:
                visit = db.IdentityVisit[self.visit_id]
                visit_user = db.IdentityVisitUser.findone(visit=visit)
                if visit_user is not None:
                    tx = visit_user.t.delete()
                    db.execute(tx)
            anon = SchevoIdentity(None, None)
            identity.set_current_identity(anon)
        finally:
            lock.release()


class SchevoIdentityProvider(object):

    def __init__(self):
        self.db = db
        def encrypt_password(pw):
            return pw
        # XXX: Add support for md5/sha1
        self.encrypt_password = encrypt_password

    def create_provider_model(self):
        # Not applicable for Schevo.
        pass

    def validate_identity(self, user_name, password, visit_key):
        """Lookup the identity represented by user_name and determine
        whether the password is correct.

        Must return either None if the credentials weren't valid
        or an object containing the following properties:

            user_name: original user name
            user: a provider dependant user object
            groups: set of group names
            permissions: set of permission names
        """
        user = self.db.IdentityUser.findone(name=user_name)
        if not user:
            log.warning('No such user: %s', user_name)
            return None
        if not self.validate_password(user, user_name, password):
            log.info('Passwords do not match for user: %s', user_name)
            return None
        # Link the user to the visit
        lock = db.write_lock()
        try:
            visit = db.IdentityVisit.findone(key=visit_key)
            visit_user = db.IdentityVisitUser.findone(visit=visit)
            if visit_user is not None:
                tx = visit_user.t.update(user=user)
                db.execute(tx)
            else:
                tx = db.IdentityVisitUser.t.create(visit=visit, user=user)
                visit_user = db.execute(tx)
            identity = SchevoIdentity(visit.sys.oid, user)
            return identity
        finally:
            lock.release()

    def validate_password(self, user, user_name, password):
        lock = db.read_lock()
        try:
            return (
                user.enabled
                and user.password == self.encrypt_password(password)
                )
        finally:
            lock.release()

    def load_identity(self, visit_key):
        lock = db.read_lock()
        try:
            visit = db.IdentityVisit.findone(key=visit_key)
            return SchevoIdentity(visit.sys.oid)
        finally:
            lock.release()

    def anonymous_identity(self):
        return SchevoIdentity(None)


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
