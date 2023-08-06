#-------------------------------------------------------------------------
# Copyright 2009-2010 David Isaacson, Stou Sandalski, Information Capsid
# Pylons template Copyright (c) 2005-2009 Ben Bangert, James Gardner, Philip Jenvey and contributors.
#
# This file is part of the program Adjector.
#
# Adjector is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) version 3 of the License.
#
# Adjector is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Adjector. If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------
'''
The base Controller
'''
import logging

import adjector.forms as forms #IGNORE:W0611
import adjector.model as model #IGNORE:W0611

from datetime import datetime, timedelta
from pylons import g, request, response, session, tmpl_context as c #IGNORE:W0611
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, redirect_to #IGNORE:W0611
from pylons.decorators import rest #pylint: disable-msg=E0611,W0611
from paste.recursive import ForwardRequestException #pylint: disable-msg=E0611,W0611
from pylons.templating import render #IGNORE:W0611
from sqlalchemy import and_, asc, desc, func, or_ #IGNORE:W0611
from tw.api import WidgetBunch #IGNORE:W0611
from tw.mods.pylonshf import validate #IGNORE:W0611
from webob.exc import HTTPNotFound

from adjector.core.conf import conf #IGNORE:W0611
from adjector.model import meta
from adjector.model.entities import CircularDependencyException
from adjector.lib import helpers as h #IGNORE:W0611
from adjector.lib.precache import precache_zone
from adjector.lib.util import FormProxy

log = logging.getLogger(__name__)

class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        '''Invoke the Controller'''
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            meta.Session.remove()
            
    def __init__(self):
        WSGIController.__init__(self)
        
        if session.has_key('message'):
            c.session_message = session['message']
            del session['message']
            session.save()
            
    def _on_updates(self, updated):
        ''' Do things to dirty objects '''
        
        # precaching
        creatives = [obj for obj in updated if isinstance(obj, model.Creative)]        
        zones = [obj for obj in updated if isinstance(obj, model.Zone)]
        
        # if no creatives modified, we only have to modify the changed zones
        if not creatives:
            return [precache_zone(zone) for zone in zones]

        # If creatives modified, we need to figure out what zones they belonged to
        # and totally redo those
        for creative in creatives:
            for pair in creative.creative_zone_pairs:
                zones.append(pair.zone)

        # now that we know what zones we *definitely* need to refresh...
        for zone in model.Zone.query():
            if zone in zones:
                # totally redo all weights for this zone
                precache_zone(zone)
            
            else:
                # only redo if the creatives NOW will be in that zone
                precache_zone(zone, [c.id for c in creatives])
        
class ObjectController(BaseController):
    
    native = None
    form_proxy = FormProxy()
    singular = None
    plural = None
    
    def __init__(self):
        BaseController.__init__(self)
        
        if self.form:
            self.form_proxy.set(self.form)
            
    def _obj(self, id):
        obj = self.native.get(int(id))
        if obj is None:
            raise HTTPNotFound('%s not found' % self.singular.title())
        return obj

    def list(self):
        query = self.native.query()
        setattr(c, self.plural, self.native.query())
        c.title = self.plural.title()
        return render('list.%s' % self.plural)
    
    @rest.dispatch_on(POST='do_edit')
    def view(self, id):
        obj = self._obj(id)
        setattr(c, self.singular, obj)
        child_args = dict(parent_id=dict(options=[''] + obj.possible_parents(obj)))
        c.form = self.form(action=h.url_for(), value=obj.value(), child_args=child_args, edit=True)
        c.title = obj.title
        return render('view.%s' % self.singular)

    @rest.dispatch_on(POST='do_new')
    def new(self):
        child_args = dict(parent_id=dict(options=[''] + self.native.possible_parents()))
        c.form = self.form(action=h.url_for(), value=dict(request.params), child_args=child_args, edit=False)
        c.title = 'New %s' % self.singular.title()
        return render('common.form')

    @rest.restrict('POST')
    @validate(form=form_proxy, error_handler='new') #pylint: disable-msg=E0602
    def do_new(self):
        try:
            obj = self.native(self.form_result)
            model.session.commit()
            self._on_updates(obj._updated)
            session['message'] = 'Changes saved.'
        except CircularDependencyException:
            model.session.rollback()
            session['message'] = 'Assigning that set/location creates a cycle.  Don\'t do that!'
        
        session.save()
        return redirect_to(obj.view())

    @rest.restrict('POST')
    @validate(form=form_proxy, error_handler='view') #pylint: disable-msg=E0602
    def do_edit(self, id):
        obj = self._obj(id)

        if request.POST.has_key('delete'):
            self._delete(self, obj)
        try:
            updates = obj.set(self.form_result)            
            model.session.commit()
            self._on_updates(updates)
            session['message'] = 'Changes saved.'
        except CircularDependencyException:
            model.session.rollback()
            session['message'] = 'Assigning that set/location creates a cycle.  Don\'t do that!'
        
        session.save()
        return redirect_to(obj.view())
    
    def _delete(self, obj):
        obj.delete()
        model.session.commit()
        session['message'] = '%s deleted.' % self.singular.title()
        session.save()
        return redirect_to(h.url_for(action='list'))
        
    
class ContainerObjectController(ObjectController):
    
    def list(self):
        setattr(c, self.plural, self.native.query.filter_by(parent_id=None))
        c.title = self.plural.title()
        return render('list.%s' % self.plural)

    def _delete(self, obj):
        updated = obj.delete()
        model.session.commit()
        _on_updates(self, updated)
        
        session['message'] = '%s deleted.' % self.singular.title()
        session.save()
        return redirect_to(h.url_for(action='list'))
