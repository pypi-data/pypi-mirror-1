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
"""Pylons environment configuration"""
import os

#from genshi.template import TemplateLoader
from pylons import config
from sqlalchemy import engine_from_config

import adjector.lib.app_globals as app_globals
import adjector.lib.helpers

from adjector.config.routing import make_map
from adjector.core.conf import conf

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='adjector', template_engine=None, paths=paths)

    # Load config - has to be done before routing

    config['pylons.app_globals'] = app_globals.Globals()
    config['pylons.h'] = adjector.lib.helpers

    # Create the Genshi TemplateLoader
    genshi_options = {'genshi.default_doctype': 'xhtml-strict',
                      'genshi.default_format': 'xhtml',
                      'genshi.default_encoding': 'UTF-8',
                      'genshi.max_cache_size': 250,
                     }
    
    config.add_template_engine('genshi', 'adjector.templates', genshi_options)
    #config['pylons.app_globals'].genshi_loader = TemplateLoader(
    #    paths['templates'], auto_reload=True)
    
    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    conf.load(config)
    config['pylons.app_globals'].conf = conf

    # Setup the SQLAlchemy database engine
    # If we put this here, we can load our config *first*
    from adjector.model import init_model
    engine = engine_from_config(config, 'sqlalchemy.')
    init_model(engine)

    # Setup routing *after* config options parsed
    config['routes.map'] = make_map()
