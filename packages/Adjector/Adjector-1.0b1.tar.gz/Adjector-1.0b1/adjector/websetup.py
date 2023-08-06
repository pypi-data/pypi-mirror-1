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
"""Setup the adjector application"""
import elixir
import logging

from pylons import config

from adjector.config.environment import load_environment
from adjector.core.conf import conf as adjector_conf
from adjector.lib.util import import_module
from adjector.lib.precache import precache_zone

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup adjector here"""
    load_environment(conf.global_conf, conf.local_conf)

    # This has to be *after* the environment is loaded, otherwise our options don't make it to the model
    import adjector.model as model
    from adjector.model import meta
    # Create the tables if they don't already exist
    meta.metadata.create_all(bind=meta.engine)
    elixir.create_all(meta.engine)
    
    # Import initial data, if it exists
    if adjector_conf.initial_data:
        try:
            module = import_module(adjector_conf.initial_data)
            
            print 'Importing initial data...'
            
            if hasattr(module, 'sets'):
                print '  Importing %i sets' % len(module.sets)
                for set in module.sets:
                    model.Set(set)
                    model.session.commit()
            if hasattr(module, 'creatives'):
                print '  Importing %i creatives' % len(module.creatives)
                for creative in module.creatives:
                    model.Creative(creative)
            if hasattr(module, 'locations'):
                print '  Importing %i locations' % len(module.locations)
                for location in module.locations:
                    model.Location(location)
                    model.session.commit()
            if hasattr(module, 'zones'):
                print '  Importing %i zones' % len(module.zones)
                for zone in module.zones:
                    model.Zone(zone)
            model.session.commit()
            
            print '  Done'

            print 'Precaching...'
            for zone in model.Zone.query():
                precache_zone(zone)
            
            print '  Done'
        
        except ImportError:
            log.warn('Could not find example data.')
