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

import pylons

from paste.deploy import loadapp
from webob.exc import HTTPNotFound

#from paste.recursive import Includer

from adjector.core.conf import conf

class AdjectorMiddleware(object):
    def __init__(self, app, config):
        self.app = app
        
        #raw_config = appconfig('config:%s' % config['__file__'], name='adjector')
        #self.path = adjector_config_raw.local_conf.get('base_url', '/adjector')
        
        self.adjector_app  = loadapp('config:%s' % config['__file__'], name='adjector')
        self.path = conf.base_url
    
        # Remove the adjector config from the config stack; otherwise the host app gets *very* confused
        # We should be done initializing adjector, so this isn't used again anyways.  
        # The RegistryMiddleware takes care of this from now on (during requests).
        process_configs = pylons.config._process_configs
        adjector_dict = [dic for dic in process_configs if dic['pylons.package'] == 'adjector'][0]
        process_configs.remove(adjector_dict)
    
    def __call__(self, environ, start_response):
        if self.path and environ['PATH_INFO'].startswith(self.path):
            #environ['PATH_INFO'] = environ['PATH_INFO'][len(self.path):] or '/'
            #environ['SCRIPT_NAME'] = self.path
            return self.adjector_app(environ, start_response)

        else:
            #environ['adjector.app'] = self.adjector_app
            #environ['adjector.include'] = Includer(self.adjector_app, environ, start_response)
            return self.app(environ, start_response)

def make_middleware(app, global_conf, **app_conf):
    return AdjectorMiddleware(app, global_conf)

def null_middleware(global_conf, **app_conf):
    return lambda app: app

class FilterWith(object):
    def __init__(self, app, filter, path):
        self.app = app
        self.filter = filter
        self.path = path
    
    def __call__(self, environ, start_response):
        if self.path and environ['PATH_INFO'].startswith(self.path):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.path):] or '/'
            environ['SCRIPT_NAME'] += self.path
            return self.filter(environ, start_response)
        else:
            return self.app(environ, start_response)
        
class FilteredApp(object):
    ''' 
    Only allow access when path_info starts with 'path', otherwise throw 404
    This can't be a subclass of StaticURLParser because that creates new instances of its __class__ '''
    def __init__(self, app, path):
        self.app = app
        self.path = path
    
    def __call__(self, environ, start_response):
        if self.path and environ['PATH_INFO'].startswith(self.path):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.path):] or '/'
            environ['SCRIPT_NAME'] += self.path
            return self.app(environ, start_response)
        else:
            raise HTTPNotFound()

class StripTrailingSlash(object):
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        environ['PATH_INFO'] = environ.get('PATH_INFO', '').rstrip('/')
        return self.app(environ, start_response)