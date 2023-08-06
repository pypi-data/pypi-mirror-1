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

import pytz, re, time
from datetime import datetime

cj_link_tz = pytz.timezone('US/Pacific') # CJ links use Pacific Time, including Daylight Savings
# Note that CJ Stats (from the API) use UTC, so they'll probably need a separate date function once we start importing them

def from_cj_date(string):
    if not string:
        return None
    format = '%Y-%m-%d %H:%M:%S'
#    dt = datetime.strptime(string.split('.')[0], format)
    dt = datetime(*(time.strptime(string.split('.')[0], format)[0:6]))
    return cj_link_tz.localize(dt)

def to_cj_date(date):
    if not date:
        return ''
    return date.strftime('%m/%d/%Y')

def remove_tracking_cj(string, id):
    if id is None:
        return string
    return re.sub(str(id), '0', string)