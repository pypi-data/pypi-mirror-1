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

class CreativeController(ObjectController):
    
    native = model.Creative
    form = forms.Creative
    singular = 'creative'
    plural = 'creatives'
    
    def _delete(self, creative):
        zones = creative.zones
        obj.delete()
        model.session.commit()
        
        for zone in zones:
            precache_zone(zone) # with no more creative, the probabilities will be different of course
        
        session['message'] = '%s deleted.' % self.singular.title()
        session.save()
        return redirect_to(h.url_for(action='list'))
