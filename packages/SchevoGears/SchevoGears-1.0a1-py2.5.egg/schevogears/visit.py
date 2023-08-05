"""schevogears visit support.

For copyright, license, and warranty, see bottom of file.
"""

from datetime import datetime, timedelta

import cherrypy
from turbogears.util import DictObj
import turbogears.visit.api as visitapi

from schevogears.database import package_database

import logging
log = logging.getLogger('turbogears.visit')


db = None


# XXX: Put somewhere else?
def schevo_to_dict(obj):
    d = obj.sys.fields().value_map()
    d['_oid'] = obj.sys.oid
    d['_rev'] = obj.sys.rev
    return d


def start_extension():
    """Overridden extension started for visitor tracking."""
    if not cherrypy.config.get('visit.on', False):
        return
    log.info('Visit tracking starting.')
    from schevogears import visit as sgvisit
    sgvisit.db = package_database()
    visitapi._manager = sgvisit.SchevoVisitManager(timedelta(0, 60 * 60))
##     sgvisit.db = package_database('turbogears.visit')
##     visitapi._manager = sgvisit.SchevoVisitManager()
    filter = sgvisit.VisitFilter()
    if not hasattr(cherrypy.root, '_cp_filters'):
        cherrypy.root._cp_filters = []
    cherrypy.root._cp_filters.append(filter)


def shutdown_extension():
    if not cherrypy.config.get('visit.on', False):
        return
    log.info('Visit tracking shutting down.')
    if visitapi._manager:
        visitapi._manager.shutdown()


class VisitFilter(visitapi.VisitFilter):

##     def before_main(self):
##         if not cherrypy.config.get('visit.on', True):
##             visitapi.set_current(None)
##             return
##         visit = self.get_visit()
##         visitapi.set_current(visit)
##         try:
##             for plugin in visitapi._plugins:
##                 plugin.record_request(visit.id)
##         except cherrypy.InternalRedirect, e:
##             cherrypy.request.object_path = e.path

    def new_visit(self):
        log.info('Creating new visit')
        now = datetime.now()
        visit_key = self._generate_key()
        tx = db.IdentityVisit.t.create(
            key=visit_key,
            expires=now + self.timeout,
            )
        visit = db.execute(tx)
        visit = DictObj(schevo_to_dict(visit))
        visit['id'] = visit['_oid']
        visit['is_new'] = True
        self.send_cookie(visit_key)
        for plugin in visitapi._plugins:
            plugin.new_visit(visit.id)
        return visit

    def get_visit(self):
        cookies = cherrypy.request.simpleCookie
        if not self.cookie_name in cookies:
            return self.new_visit()
        now = datetime.now()
        visit_key = cookies[self.cookie_name].value
        lock = db.read_lock()
        try:
            visit = db.IdentityVisit.findone(key=visit_key)
            if visit and now < visit.expires:
                visitapi._manager.update_visit(visit, now + self.timeout)
                visit = DictObj(schevo_to_dict(visit))
                visit['id'] = visit['_oid']
                visit['is_new'] = False
                return visit
            log.debug('Visit (%s) has expired', visit_key)
            return self.new_visit()
        finally:
            lock.release()


class SchevoVisitManager(visitapi.BaseVisitManager):

    def clean_queue(self):
        try:
            self.lock.acquire()
            queue = self.queue
            self.queue = dict()
            self.lock.release()
        except:
            self.lock.release()
            raise
        for visit, expires in queue.iteritems():
            if visit in db.IdentityVisit:
                tx = visit.t.update(expires=expires)
                db.execute(tx)

    def new_visit_with_key(self, visit_key):
        lock = db.write_lock()
        try:
            tx = db.IdentityVisit.t.create(
                key = visit_key,
                expires = datetime.now() + self.timeout,
                )
            db.execute(tx)
        finally:
            lock.release()
        return visitapi.Visit(visit_key, True)

    def visit_for_key(self, visit_key):
        lock = db.read_lock()
        try:
            visit = db.IdentityVisit.findone(key=visit_key)
            now = datetime.now()
            if visit is None or visit.expires < now:
                return None
            self.update_visit(visit_key, now + self.timeout)
        finally:
            lock.release()
        return visitapi.Visit(visit_key, False)

    def update_queued_visits(self, queue):
        if db is None:
            return
        lock = db.write_lock()
        try:
            db.execute(db.IdentityVisit.t.update_queued_visits(queue.items()))
        finally:
            lock.release()


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
