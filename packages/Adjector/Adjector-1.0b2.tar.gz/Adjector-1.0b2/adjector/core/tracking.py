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

import os.path
import random
import re

from adjector.core.conf import conf
from adjector.core.cj_util import remove_tracking_cj

def add_tracking(html):
    
    if re.search('google_ad_client', html):
        return add_tracking_adsense(html)
    else:
        return add_tracking_generic(html)    
            
def add_tracking_generic(html):
    def repl(match):
        groups = match.groups()
        return groups[0] + 'ADJECTOR_TRACKING_BASE_URL/track/click_with_redirect?creative_id=ADJECTOR_CREATIVE_ID&zone_id=ADJECTOR_ZONE_ID&cache_bust=' + cache_bust() + '&url=' + groups[1] + groups[2]

    html_tracked = re.sub(r'''(.*<a[^>]+href\s*=\s*['"])([^"']+)(['"][^>]*>.*)''', repl, html)
    
    if html == html_tracked: # if no change, don't touch.
        return
    else:
        return html_tracked
    
def add_tracking_adsense(html):
    adsense_tracking_code = open(os.path.join(conf.root, 'public', 'js', 'adsense_tracker.js')).read()
    
    click_track = 'ADJECTOR_TRACKING_BASE_URL/track/click_with_image?creative_id=ADJECTOR_CREATIVE_ID&zone_id=ADJECTOR_ZONE_ID&cache_bust=' # cache_bust added in js
    
    html_tracked = '''
        <span>
            %(html)s
            <script type="text/javascript"><!--// <![CDATA[
                /* adjector_click_track=%(click_track)s */
                %(adsense_tracking_code)s
            // ]]> --></script>
        </span>
        ''' % dict(html=html, adsense_tracking_code=adsense_tracking_code, click_track=click_track)
    
    return html_tracked

def cache_bust():
    return str(random.random())[2:]

def remove_tracking(html, cj_site_id = None):
    if cj_site_id:
        return remove_tracking_cj(html, cj_site_id)
    elif re.search('google_ad_client', html):
        return remove_tracking_adsense(html)
    else:
        return html # we can't do anything
    
def remove_tracking_adsense(html):
    html_notrack = '''
        <script type='text/javascript'>
            var adjector_google_adtest_backup = google_adtest;
            var google_adtest='on';
        </script>
        %(html)s
        <script type='text/javascript'>
            var google_adtest=adjector_google_adtest_backup;
        </script>
    ''' % dict(html=html)
    
    return html_notrack