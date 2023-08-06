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

from simplejson import dumps as jsonify
import adjector.model as model

class FormProxy:
    ''' A simple class that allows the use of @validate in base classes '''
    def set(self, form):
        self.form = form

    def validate(self, *args, **kwargs):
        return self.form.validate(*args, **kwargs)

def get_stat_totals(start=None, end=None):
    clicks = model.Click.query
    views = model.View.query
    if start:
        clicks = clicks.filter(model.Click.time > start)
        views = views.filter(model.View.time > start)
        
    if end:
        clicks = clicks.filter(model.Click.time < end)
        views = views.filter(model.View.time < end)

    return views.count(), clicks.count()
    
#http://www.siafoo.net/snippet/259
def import_module(name):
    module = __import__(name)
    if '.' in name:
        for segment in name.split('.')[1:]:
            module = getattr(module, segment)
    return module
        
def print_date(date):
    if date is None:
        return ''
    return date.strftime('%Y-%m-%d %H:%M:%S')

