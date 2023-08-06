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
#from pylons import request
from sqlalchemy import engine_from_config

from adjector.core.conf import conf
from adjector.core.render import render_zone as lib_render_zone
from adjector.model import init_model, meta

log = logging.getLogger(__name__)

def initialize_adjector(config):
    ''' You only need to call this if you aren't using the middleware.  
    SA db setup is done for you by loading the adjector app in the middleware.  Apparently.
    
    You also have the option of loading the config manually, and providing your own sa engine.
    Load data with adjector.core.conf.conf.load(config); assign engine with adjector.model.meta.engine = engine'''

    # Setup the SQLAlchemy database engine
    if not config.has_key('sqlalchemy.url'):
        raise Exception('You need to specify an sqlalchemy.url in your config data.')

    engine = engine_from_config(config, 'sqlalchemy.')
    init_model(engine)
    
    conf.load(config)

#def render_zone(id, track=None, admin=False): # None = use default
#    includer = request.environ['adjector.include']
#    response = includer('/zone/%i/render' % id, extra_environ = {'adjector.options': {'track': track, 'admin': admin}})
#    return response.str

def render_zone(ident, track=None, admin=False): # None = use default
    ''' You better have initialzed the db before calling this '''
    
    if meta.engine is None:
        log.error('Adjector SQLAlchemy database engine not initialized.  You cannot use this function.')
        return ''

    if not conf.loaded: # assume if you've managed this the db is loaded too
        log.error('Adjector configuration not loaded.  You cannot use this function')
        return ''
        
    html =  lib_render_zone(ident, track, admin)
    meta.Session.remove()
    return html

