#-------------------------------------------------------------------------
# Copyright 2009-2010 David Isaacson, Stou Sandalski, Information Capsid
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

import logging
import re

from paste.deploy.converters import asbool

from adjector.core.render import render_zone
from adjector.lib.base import *

log = logging.getLogger(__name__)

class ZoneController(ObjectController):
    
    native = model.Zone
    form = forms.Zone
    singular = 'zone'
    plural = 'zones'
        
    @rest.dispatch_on(POST='do_edit')
    def view(self, id):
        obj = self._obj(id)
        setattr(c, self.singular, obj)
        
        value=obj.value()
        value['preview'] = c.render = h.Markup(render_zone(id, track=False))
        child_args = dict(parent_id=dict(options=[''] + obj.possible_parents()))
        
        c.form = self.form(action=h.url_for(), value = value, child_args=child_args, edit=True)
        c.title = obj.title
        return render('view.zone')
    
    def render(self, ident):
        options = request.environ.get('adjector.options', {})
        if request.params.has_key('track'):
            options['track'] = asbool(request.params.has_key('track'))
        if request.params.has_key('admin'):
            options['admin'] = asbool(request.params.has_key('admin'))
        
        return render_zone(ident, **options)
    
    def render_js(self, ident):
        ''' 
        Render ads through a javascript tag
        
        Usage Example:
        <script type='text/javascript' src='http://localhost:5000/RENDER_BASE_URL/zone/NAME/render.js?track=0' />
        Where RENDER_BASE_URL is the url you specified in your .ini file and NAME is your ad name.
        '''
        options = request.environ.get('adjector.options', {})
        if request.params.has_key('track'):
            options['track'] = asbool(request.params['track'])
        if request.params.has_key('admin'):
            options['admin'] = asbool(request.params['admin'])

        rendered = render_zone(ident, **options)

        wrapper = '''document.write('%s')'''
        
        # Do some quick substitutions to inject... #TODO there must be an existing function that does this
        rendered = re.sub(r"'", r"\'", rendered) # escape quotes
        rendered = re.sub(r"[\r\n]", r"", rendered) # remove line breaks
        
        response.headers['content-type'] = 'text/javascript; charset=utf8'
        return wrapper % rendered
