#-------------------------------------------------------------------------
# Copyright 2009-2010 David Isaacson, Stou Sandalski, Information Capsid
# Pylons template Copyright (c) 2005-2009 Ben Bangert, James Gardner, Philip Jenvey and contributors.
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
"""The application's model objects"""

import elixir
import logging

# Set up meta
from adjector.core.conf import conf as adj_conf
if hasattr(adj_conf, 'meta'):
    # if we have one, use this meta instead
    meta = adj_conf.meta
else:
    import meta

# Set up entities; start logging
import entities # for later, pretty sure above the * is faster
from entities import *

log = logging.getLogger(__name__)

elixir.setup_all()

# Get session for later use
session = meta.Session

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    
    meta.Session.configure(bind=engine)
    meta.engine = engine
    meta.metadata.bind = engine
    #engine.echo = False