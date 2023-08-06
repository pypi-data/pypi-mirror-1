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
''' A container for a global dictionary-like object.  To replace pylons's g because this might not always be called by pylons '''

import os
import logging
import pytz
from ConfigParser import SafeConfigParser

from adjector.core.contrib.converters import asbool # This removes a paste dependency for clients

log = logging.getLogger(__name__)

class ConfigObject:
    
    loaded = False
    table_prefix = ''
    
    def load(self, raw):
        self.loaded = True
        self.root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_url = raw.get('base_url', '').rstrip('/')
        self.admin_base_url = raw.get('admin_base_url', '').rstrip('/') or self.base_url
        self.render_base_url = raw.get('render_base_url', '').rstrip('/') or self.base_url
        self.tracking_base_url = raw.get('tracking_base_url', '').rstrip('/')  or self.base_url
        
        self.table_prefix = raw.get('table_prefix', '')
        
        self.timezone = pytz.timezone(raw.get('timezone', 'US/Pacific'))
        
        self.enable_adjector_view_tracking = asbool(raw.get('enable_adjector_view_tracking', True))
        self.enable_adjector_click_tracking = asbool(raw.get('enable_adjector_click_tracking', True))
        self.enable_third_party_tracking = asbool(raw.get('enable_third_party_tracking', True))
        self.enable_cj_site_replacements = asbool(raw.get('enable_cj_site_replacements', True))
        self.require_javascript = asbool(raw.get('require_javascript', True))
        self.initial_data = raw.get('initial_data') #This isn't actually needed except in websetup
        
        # Parse .ini file (can't use paste's parser apparently)
        if raw.get('cj_data'):
            try:
                parser = SafeConfigParser(dict(here = os.path.dirname(raw['cj_data'])))
                parser.read(raw['cj_data'])
            except IOError, err:
                raise IOError('Could not open file specified by cj_data: %s.  Error: %s' %(raw['cj_data'], err))

            cj_data = dict(parser.items(parser.sections()[0]))
            self.cj_api_key = cj_data.get('cj_api_key')
            self.cj_site_id = cj_data.get('cj_site_id')
            
        else:
            self.cj_api_key = raw.get('cj_api_key')
            self.cj_site_id = raw.get('cj_site_id')
            
    def load_from(self, config):
        parser = SafeConfigParser(dict(here = os.path.dirname(config['__file__'])))
        parser.read(config['__file__'])
        
        section = None
        if parser.has_section('app:adjector'):
            section = 'app:adjector'
        else:
            for sect in parser.sections():
                if sect.contains(':adjector'):
                    section = sect
                    break
        
        if section is None:
            log.error('Could not find an adjector section in the file %s' % config['__file__'])
            return
        
        raw = dict(parser.items(section))
        self.load(raw)
        
conf = ConfigObject()
