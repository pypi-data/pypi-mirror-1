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
"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
import logging

from pylons import config
from routes import Mapper

from adjector.core.conf import conf

log = logging.getLogger(__name__)

def intify(*keys):
    ''' 
    Make vars into integers 
    '''

    def container(environ, result):
        for key in keys:
            if result.get(key) is None:
                continue
            
            if result[key].isdigit():
                result[key] = int(result[key])
            else:
                log.error('%s was sent to intify method but is not in digit form' % result[key])
                result[key] = None
        return True
    return dict(function=container)

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'], always_scan=config['debug'])
    map.minimization = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')
    
    base = conf.admin_base_url

    # CUSTOM ROUTES HERE
    map.redirect(base, base + '/')
    map.connect(base + '/', controller='main', action='index')
    
    map.connect(base + '/import/cj', controller='cj', action='start')
    map.connect(base + '/import/cj/{action}', controller='cj')
    map.connect(base + '/import/cj/{site_id}/{id}/{action}', controller='cj', requirements=dict(site_id='\d+', id='\d+')) #note that i am not intifying this on purpose
    map.connect(base + '/new/{controller}', action='new')
    map.connect(base + '/stats', controller='stats', action='index')
    
    map.connect(conf.render_base_url + '/zone/{ident}/render', controller='zone', action='render')
    map.connect(conf.render_base_url + '/zone/{ident}/render.js', controller='zone', action='render_js')
    
    map.connect(conf.tracking_base_url + '/track/{action}', controller='track')
    
    map.connect(base + '/{controller}', action='list')
    map.connect(base + '/{controller}/{id}', action='view', requirements=dict(id='\d+'), conditions=intify('id'))
    map.connect(base + '/{controller}/{action}', requirements=dict(controller='(?!tracking)'))
    map.connect(base + '/{controller}/{id}/{action}', requirements=dict(id='\d+'), conditions=intify('id'))

    return map
