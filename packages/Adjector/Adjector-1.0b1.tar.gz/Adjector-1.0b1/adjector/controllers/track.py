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

from adjector.lib.base import *

log = logging.getLogger(__name__)

class TrackController(BaseController):
    
    def _register_click(self):
        if request.params.has_key('creative_id') and request.params.has_key('zone_id'):
            model.Click(request.params['creative_id'], request.params['zone_id'])
            model.session.commit()
            
    def click_with_image(self):
        self._register_click()
        return #TODO: return an image? might be a good idea

    def click_with_redirect(self):
        self._register_click()
        return redirect_to(str(request.params.get('url', '/')))