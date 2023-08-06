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

from __future__ import division

import os
from datetime import datetime
from ConfigParser import SafeConfigParser
from cProfile import Profile

from adjector.client import initialize_adjector, render_zone

from adjector.tests import *

class TestRenderController(TestController):
    
    def __before__(self):
        ini = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'development.ini')
        parser = SafeConfigParser(dict(here = os.path.dirname(ini)))
        parser.read(ini)
        initialize_adjector(dict(parser.items('app:adjector')))

    def test_performance(self):
        profile = Profile()
        
        def loop():
            count = 500
            start = datetime.now()
            for i in xrange(count):
                if i % 100 == 0:
                    print 'Test #%i' % i
                render_zone(1)
        
            diff = datetime.now() - start
            print 'Average rendering time: %s ms' % ((diff.seconds * 1000 + diff.microseconds / 1000) / count) 
            
        profile.runcall(loop)
        print profile.print_stats('time')       
