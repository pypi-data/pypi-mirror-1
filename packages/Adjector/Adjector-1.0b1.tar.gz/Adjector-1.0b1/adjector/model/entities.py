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

from datetime import datetime
from elixir import using_options, using_table_options, BLOB, Boolean, ColumnProperty, \
                    DateTime, Entity, EntityMeta, Field, Float, Integer, ManyToMany, ManyToOne, \
                    OneToMany, OneToOne, SmallInteger, String, UnicodeText
from genshi import Markup
from sqlalchemy import func, UniqueConstraint

from adjector.core.conf import conf
from adjector.core.tracking import add_tracking, remove_tracking

log = logging.getLogger(__name__)

max_int = 2147483647
tz_now = lambda : datetime.now(conf.timezone)

UnicodeText = UnicodeText(assert_unicode=False)

class CircularDependencyException(Exception):
    pass

class GenericEntity(object):
    def __init__(self, data):
        self._updated = self.set(data)
                
    def set(self, data):
        for field in data.keys():
            if hasattr(self, field):
                if field == 'title':
                    data[field] = data[field][:80]
                self.__setattr__(field, data[field])
            else:
                log.warning('No field: %s' % field)
    
    def value(self):
        return self.__dict__
    
class GenericListEntity(GenericEntity):
    def set(self, data):
        GenericEntity.set(self, data)

        # Detect cycles in parenting - Brent's algorithm http://www.siafoo.net/algorithm/11
        turtle = self
        rabbit = self
        
        steps_taken = 0
        step_limit = 2
        
        while True:
            if not rabbit.parent_id:
                break #no loop
            rabbit = rabbit.query.get(rabbit.parent_id)
            
            steps_taken += 1
            
            if rabbit == turtle:
                # loop!
                raise CircularDependencyException
            
            if steps_taken == step_limit:
                steps_taken = 0
                step_limit *=2
                turtle = rabbit
                
class CJIgnoredLink(Entity):
    cj_advertiser_id = Field(Integer, required=True)
    cj_link_id = Field(Integer, required=True)

    using_options(tablename=conf.table_prefix + 'cj_ignored_links') 
    using_table_options(UniqueConstraint('cj_link_id'))
    
    def __init__(self, link_id, advertiser_id):
        self.cj_advertiser_id = advertiser_id
        self.cj_link_id = link_id
                
class Click(Entity):
    
    time = Field(DateTime(timezone=True), required=True, default=tz_now)   
    creative = ManyToOne('Creative', ondelete='set null')
    zone = ManyToOne('Zone', ondelete='set null')
    
    using_options(tablename=conf.table_prefix + 'clicks')
    
    def __init__(self, creative_id, zone_id):
        self.creative_id = creative_id
        self.zone_id = zone_id

class Creative(GenericEntity, Entity):
    
    parent = ManyToOne('Set', required=False, ondelete='set null')
    #zones = ManyToMany('Zone', tablename='creatives_to_zones')
    creative_zone_pairs = OneToMany('CreativeZonePair', cascade='delete')
    
    title = Field(String(80, convert_unicode=True), required=True)
    html = Field(UnicodeText, required=True, default='')
    is_text = Field(Boolean, required=True, default=False)
    
    width = Field(Integer, required=True, default=0) 
    height = Field(Integer, required=True, default=0)
    
    start_date = Field(DateTime(timezone=True))
    end_date = Field(DateTime(timezone=True))
    weight = Field(Float, required=True, default=1.0)
    add_tracking = Field(Boolean, required=True, default=True)
    disabled = Field(Boolean, required=True, default=False)
    
    create_date = Field(DateTime(timezone=True), required=True, default=tz_now)

    cj_link_id = Field(Integer)
    cj_advertiser_id = Field(Integer)
    cj_site_id = Field(Integer)
    
    views = OneToMany('View')
    clicks = OneToMany('Click')

    # Cached Values
    html_tracked = Field(UnicodeText) #will be overwritten on set
    parent_weight = Field(Float, required=True, default=1.0) # overwritten on any parent weight change

    using_options(tablename=conf.table_prefix + 'creatives', order_by='title')
    using_table_options(UniqueConstraint('cj_link_id'))
    
    def __init__(self, data):
        GenericEntity.__init__(self, data)
        if self.parent_id:
            self.parent_weight = Set.get(self.parent_id).weight
            
    def get_clicks(self, start=None, end=None):
        query = Click.query.filter_by(creative_id = self.id)
        if start:
            query = query.filter(Click.time > start)
        if end:
            query = query.filter(Click.time < end)
        return query.count()

    def get_views(self, start=None, end=None):
        query = View.query.filter_by(creative_id = self.id)
        if start:
            query = query.filter(View.time > start)
        if end:
            query = query.filter(View.time < end)
        return query.count()

    @staticmethod
    def possible_parents(this=None):
        return [[set.id, set.title] for set in Set.query()]
    
    def set(self, data):
        old_parent_id = self.parent_id
        old_html = self.html
        old_add_tracking = self.add_tracking
        GenericEntity.set(self, data)
        
        if self.parent_id != old_parent_id:
            self.parent_weight = Set.get(self.parent_id).weight

        # TODO: Handle Block / Text bullshit
        # Parse html
        if self.html != old_html or self.add_tracking != old_add_tracking:
            if self.add_tracking is not False:
                self.html_tracked = add_tracking(self.html)
            else:
                self.html_tracked = None
                
        return [self]
    
    def value(self):
        value = GenericEntity.value(self)
        value['preview'] = Markup(remove_tracking(self.html, self.cj_site_id))
        value['total_weight'] = self.weight * self.parent_weight
        value['html_tracked'] = value['html_tracked'] or value['html']
        return value
    
    def view(self):
        return '%s/creative/%i' % (conf.admin_base_url, self.id)
    
class CreativeZonePair(GenericEntity, Entity):
    
    creative = ManyToOne('Creative', ondelete='cascade', use_alter=True)
    zone = ManyToOne('Zone', ondelete='cascade', use_alter=True)
    is_text = Field(Boolean, required=True)

    lower_bound = Field(Float, required=True)
    upper_bound = Field(Float, required=True)

    using_options(tablename=conf.table_prefix + 'creative_zone_pairs')
    using_table_options(UniqueConstraint('creative_id', 'zone_id'))
    
class Location(GenericListEntity, Entity):
    ''' A container for locations or zones '''
    
    parent = ManyToOne('Location', required=False, ondelete='set null')
    sublocations = OneToMany('Location')
    zones = OneToMany('Zone')
    
    title = Field(String(80, convert_unicode=True), required=True)
    description = Field(UnicodeText)

    create_date = Field(DateTime(timezone=True), required=True, default=tz_now)
    
    cj_site_id = Field(Integer)
    parent_cj_site_id = Field(Integer)
    
    using_options(tablename=conf.table_prefix + 'locations', order_by='title')

    def __init__(self, data):
        GenericEntity.__init__(self, data)
        if self.parent_id:
            self.parent_cj_site_id = Location.get(self.parent_id).cj_site_id
            
    def delete(self, data):
        updated = []
        for subloc in self.sublocations:
            updated.extend(subloc.set(dict(parent_cj_site_id = None)))
        for zone in self.zones:
            updated.extend(zone.set(dict(parent_cj_site_id = None)))
        Entity.delete(self)
        return updated

    @staticmethod
    def possible_parents(this = None):
        filter = None
        if this:
            filter = Location.id != this.id
        return [[location.id, location.title] for location in Location.query.filter(filter)]
    
    def set(self, data):
        updated = [self]
        old_parent_id = self.parent_id
        old_cj_site_id = self.cj_site_id
        old_parent_cj_site_id = self.parent_cj_site_id
        
        GenericEntity.set(self, data)
        
        if self.parent_id != old_parent_id:
            self.parent_cj_site_id = Location.get(self.parent_id).cj_site_id
        
        if self.cj_site_id != old_cj_site_id or self.parent_cj_site_id != old_parent_cj_site_id:
            # Only pass parent- down if we don't have our own
            for subloc in self.sublocations:
                updated.extend(subloc.set(dict(parent_cj_site_id = self.cj_site_id or self.parent_cj_site_id)))
            for zone in self.zones:
                updated.extend(zone.set(dict(parent_cj_site_id = self.cj_site_id or self.parent_cj_site_id)))
        
        return updated

    def view(self):
        return '%s/location/%i' % (conf.admin_base_url, self.id)
    
class Set(GenericListEntity, Entity):
    
    parent = ManyToOne('Set', required=False, ondelete='set null')
    subsets = OneToMany('Set')
    creatives = OneToMany('Creative')
    
    title = Field(String(80, convert_unicode=True), required=True)
    description = Field(UnicodeText)

    weight = Field(Float, required=True, default=1.0)
    parent_weight = Field(Float, required=True, default=1.0) # overwritten on any parent weight change

    create_date = Field(DateTime(timezone=True), required=True, default=tz_now)
    
    cj_advertiser_id = Field(Integer)
    
    using_options(tablename=conf.table_prefix + 'sets', order_by='title')
    using_table_options(UniqueConstraint('cj_advertiser_id'))

    def __init__(self, data):
        GenericEntity.__init__(self, data)
        if self.parent_id:
            self.parent_weight = Set.get(self.parent_id).weight
            
    def delete(self, data):
        updated = []
        for subset in self.subsets:
            updated.extend(subset.set(dict(parent_weight = 1.0)))
        for creative in self.creatives:
            updated.extend(creative.set(dict(parent_weight = 1.0)))
        Entity.delete(self)
        return updated

    @staticmethod
    def possible_parents(this = None):
        filter = None
        if this:
            filter = Set.id != this.id
        return [[set.id, set.title] for set in Set.query.filter(filter)]

    def set(self, data):
        updated = [self]
        old_parent_id = self.parent_id
        old_weight = self.weight
        old_parent_weight = self.parent_weight
        
        GenericEntity.set(self, data)
        
        if self.parent_id != old_parent_id:
            self.parent_weight = Set.get(self.parent_id).weight
        
        if self.weight != old_weight or self.parent_weight != old_parent_weight:
            for subset in self.subsets:
                updated.extend(subset.set(dict(parent_weight = self.parent_weight * self.weight)))
            for creative in self.creatives:
                updated.extend(creative.set(dict(parent_weight = self.parent_weight * self.weight)))

        return updated
        
    def value(self):
        value = GenericEntity.value(self)
        value['total_weight'] = self.weight * self.parent_weight
        return value

    def view(self):
        return '%s/set/%i' % (conf.admin_base_url, self.id)
        
class View(GenericEntity, Entity):
    
    time = Field(DateTime(timezone=True), required=True, default=tz_now)
    creative = ManyToOne('Creative', ondelete='set null')
    zone = ManyToOne('Zone', ondelete='set null')
    
    using_options(tablename=conf.table_prefix + 'views')

    def __init__(self, creative_id, zone_id):
        self.creative_id = creative_id
        self.zone_id = zone_id
         
class Zone(GenericEntity, Entity):
    
    parent = ManyToOne('Location', required=False, ondelete='set null')
    creative_zone_pairs = OneToMany('CreativeZonePair', cascade='delete')

    name = Field(String(80, convert_unicode=True), required=False)
    title = Field(String(80, convert_unicode=True), required=True)
    description = Field(UnicodeText)
    #creatives = ManyToMany('Creative', tablename='creatives_to_zones')
    normalize_by_container = Field(Boolean, required=True, default=False)
    
    creative_types = Field(SmallInteger, required=True, default=0) #0: Both, 1: Text, 2: Blocks 
    # These only matter if blocks allowed
    min_width = Field(Integer, required=True, default=0)
    max_width = Field(Integer, required=True, default=max_int)
    min_height = Field(Integer, required=True, default=0)
    max_height = Field(Integer, required=True, default=max_int)

    # These only matter if text allowed
    num_texts = Field(SmallInteger, required=True, default=1)
    weight_texts = Field(Float, required=True, default=1.0)
    before_all_text = Field(UnicodeText)
    after_all_text = Field(UnicodeText)
    before_each_text = Field(UnicodeText)
    after_each_text = Field(UnicodeText)
    
    create_date = Field(DateTime(timezone=True), required=True, default=tz_now)

    # Cached from parent
    parent_cj_site_id = Field(Integer)
    
    # Cached from creatives
    total_text_weight = Field(Float) # i dunno, some default?  should be updated quick.

    views = OneToMany('View')
    clicks = OneToMany('Click')
                
    using_options(tablename=conf.table_prefix + 'zones', order_by='title')
    
    def __init__(self, data):
        GenericEntity.__init__(self, data)
        if self.parent_id:
            self.parent_cj_site_id = Location.get(self.parent_id).cj_site_id
            
    def get_clicks(self, start=None, end=None):
        query = Click.query.filter_by(zone_id = self.id)
        if start:
            query = query.filter(Click.time > start)
        if end:
            query = query.filter(Click.time < end)
        return query.count()

    def get_views(self, start=None, end=None):
        query = View.query.filter_by(zone_id = self.id)
        if start:
            query = query.filter(View.time > start)
        if end:
            query = query.filter(View.time < end)
        return query.count()
            
    @staticmethod
    def possible_parents(this=None):
        return [[location.id, location.title] for location in Location.query()]
    
    def set(self, data):
        if data.has_key('previous_name'): 
            del data['previous_name']
            
        old_parent_id = self.parent_id

        GenericEntity.set(self, data)

        if self.parent_id != old_parent_id:
            self.parent_cj_site_id = Location.get(self.parent_id).cj_site_id
            
        return [self]

    def value(self):
        val = self.__dict__.copy()
        val['previous_name'] = self.name
        return val

    def view(self):
        return '%s/zone/%i' % (conf.admin_base_url, self.id)
