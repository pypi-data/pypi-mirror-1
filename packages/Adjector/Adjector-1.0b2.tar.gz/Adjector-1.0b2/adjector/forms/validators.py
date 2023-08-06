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

import logging, re, time

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from paste.deploy.converters import asbool
from tw.forms.validators import FancyValidator, FormValidator, Invalid, UnicodeString, Wrapper

from adjector.core.conf import conf

AsBool = Wrapper(to_python=asbool)

log = logging.getLogger(__name__)

class DateTime(FancyValidator):
    strip = True
    end_interval = False
    
    messages = {
        'invalidDate': 'Enter a valid date of the form YYYY-MM-DD HH:MM:SS.  You may leave off anything but the year.' 
    }
    
    def _to_python(self, value, state):
        formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%Y-%m', '%Y']
        add_if_end = [None, relativedelta(seconds=59), relativedelta(days=1, seconds=-1),
                      relativedelta(months=1, seconds=-1), relativedelta(years=1, seconds=-1)]
                                                                                                
        for format, aie in zip(formats, add_if_end):
            try:
                dt = datetime(*(time.strptime(value, format)[0:6]))
                if self.end_interval and aie:
                    dt += aie
                return conf.timezone.localize(dt)
            except ValueError, e:
                log.debug('Validation error %s' % e)
        
        raise Invalid(self.message('invalidDate', state), value, state)
    
    def _from_python(self, value, state):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    
class SimpleString(UnicodeString):
    messages = {
        'invalidString': 'May only contain alphanumerics, underscores, periods, and dashes.'
    }
    
    def validate_python(self, value, state):
        UnicodeString.validate_python(self, value, state)
        
        if re.search(r'[^\w\-.]', value):
            raise Invalid(self.message('invalidString', state), value, state)
    
# From Siafoo
class UniqueValue(FormValidator):
    validate_partial_form = True

    value_field = ''
    previous_value_field = ''
    unique_test = None # A function that gets passed the new value to test for uniqueness.  should return trueish or falsish
    not_empty = True
    __unpackargs__ = ('unique_test', 'value_field', 'previous_value_field')
        
    messages = {
        'notUnique': 'You must enter a unique value'
    }
    
    def validate_partial(self, field_dict, state):
        for name in [self.value_field, self.previous_value_field]:
            if name and not field_dict.has_key(name):
                return
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        FormValidator.validate_python(self, field_dict, state)
        value = field_dict.get(self.value_field)
        previous_value = field_dict.get(self.previous_value_field)
        
        if (not self.not_empty or value == '') and value != previous_value and not self.unique_test(value):
            errors = {self.value_field: self.message('notUnique', state)}
            error_list = errors.items()
            error_list.sort()
            error_message = '<br>\n'.join(
                ['%s: %s' % (name, value) for name, value in error_list])
            raise Invalid(error_message, field_dict, state, error_dict=errors)


