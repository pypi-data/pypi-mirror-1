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
from adjector.lib.util import get_stat_totals

log = logging.getLogger(__name__)

class StatsController(BaseController):

    def index(self):
        
        c.sets = model.Set.query.filter_by(parent_id = None)
        c.creatives = model.Creative.query.filter_by(parent_id = None)
        
        c.locations = model.Location.query.filter_by(parent_id = None)
        c.zones = model.Zone.query.filter_by(parent_id = None)
        
        # times...
        now = datetime.now()
        c.start_today = datetime(now.year, now.month, now.day)
        c.start_yesterday = c.start_today - timedelta(days=1)
        c.week_ago = now - timedelta(days=7)
        c.month_ago = now - timedelta(days=30)
        
        # totals
        c.totals_today = get_stat_totals(c.start_today)
        c.totals_yesterday = get_stat_totals(c.start_yesterday, c.start_today)
        c.totals_week = get_stat_totals(c.week_ago)
        c.totals_month = get_stat_totals(c.month_ago)
        c.totals_all = get_stat_totals()
        
        c.title = 'Stats'
        return render('stats.index')