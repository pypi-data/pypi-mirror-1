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

import logging

from sqlalchemy import and_, func, or_
from sqlalchemy.sql import case, join, select, subquery

from adjector.core.conf import conf
import adjector.model as model

log = logging.getLogger(__name__)

def precache_zone(zone, only_if_creative_ids = None):
    '''
    Precache data for creatives for this Zone.  Access by id or name.
    
    Respect all zone requirements.  Use creative weights and their containing set weights to weight randomness.
    If zone.normalize_by_container, normalize creatives by the total weight of the set they are in, 
    so the total weight of the creatives directly in any set is always 1.
    If block and text ads can be shown, a decision will be made to show one or the other based on the total probability of each type of creative.
    Note that this function is called each time you update a relevant creative or zone.
    '''
    
    # Find zone site_id, if applicable.  Default to global site_id, or else None.
    cj_site_id = zone.parent_cj_site_id or conf.cj_site_id
    #print 'precaching zone %s with oici %s' % (zone.id, only_if_creative_ids)
    
    # FILTERING
    # Figure out what kind of creative we need
                            # Size filtering
    whereclause_zone = and_(or_(and_(model.Creative.width >= zone.min_width,
                                     model.Creative.width <= zone.max_width,
                                     model.Creative.height >= zone.min_height,
                                     model.Creative.height <= zone.max_height),
                                model.Creative.is_text == True),
                            # Date filtering
                            or_(model.Creative.start_date == None, model.Creative.start_date <= func.now()),
                            or_(model.Creative.end_date == None, model.Creative.end_date >= func.now()),
                            # Site Id filtering
                            or_(model.Creative.cj_site_id == None, model.Creative.cj_site_id == cj_site_id, 
                                and_(conf.enable_cj_site_replacements, cj_site_id != None, model.Creative.cj_site_id != None)),
                            # Disabled?
                            model.Creative.disabled == False)
    
    # Sanity check - this shouldn't ever happen
    if zone.num_texts == 0:
        zone.creative_types = 2

    # Filter by text or block if needed.  If you want both we do some magic later.
    # But first we will need to find out how much of each we have, weight wise.
    # Also we delete all of the ones that we won't need
    if zone.creative_types == 1:
        zone.total_text_weight = 1.0
        whereclause_zone.append(model.Creative.is_text==True)
        [model.session.delete(pair) for  pair in model.CreativeZonePair.query.filter_by(zone_id = zone.id, is_text = False)]
        
    elif zone.creative_types == 2:
        zone.total_text_weight = 0.0
        whereclause_zone.append(model.Creative.is_text==False)    
        [model.session.delete(pair) for  pair in model.CreativeZonePair.query.filter_by(zone_id = zone.id, is_text = True)]

    # Bail if the edited creative won't go in here; no sense in redoing everything...
    if only_if_creative_ids and not model.Creative.query.filter(and_(whereclause_zone, model.Creative.id in only_if_creative_ids)).first():
        return
    #print 'continuing'
    
    # WEIGHING
    creatives = model.Creative.table
    
    # First let's figure how to normalize by how many items will be displayed.  This ensures all items are displayed equally.
    # We want this to be 1 for blocks and num_texts for texts.  Also throw in the zone.weight_texts
    #items_displayed = cast(creatives.c.is_text, Integer) * (zone.num_texts - 1) + 1
    text_weight_adjust = case([(True, zone.weight_texts / zone.num_texts), (False, 1)], creatives.c.is_text)

    if zone.normalize_by_container:
        # Find the total weight of each parent in order to normalize
        parent_weights = subquery('parent_weight', 
                                  [creatives.c.parent_id, func.sum(creatives.c.parent_weight * creatives.c.weight).label('pw_total')],
                                  group_by=creatives.c.parent_id)
        
        # Join creatives table and normalized weight table - I'm renaming fields here to make life easier down the line
        # SA was insisting on doing a full subquery anyways (I just wanted a join)
        c1 = subquery('c1', 
                      [creatives.c.id.label('id'), creatives.c.is_text.label('is_text'),
                       (creatives.c.weight * creatives.c.parent_weight * text_weight_adjust / 
                            case([(parent_weights.c.pw_total > 0, parent_weights.c.pw_total)], else_ = None)).label('normalized_weight')], # Make sure we can't divide by 0
                       whereclause_zone, # here go our filters
                       from_obj=join(creatives, parent_weights, or_(creatives.c.parent_id == parent_weights.c.parent_id,
                                                                and_(creatives.c.parent_id == None, parent_weights.c.parent_id == None)))).alias('c1')

    else:
        # We don't normalize weight by parent weight, so we dont' need fancy joins
        c1 = subquery('c1', 
                       [creatives.c.id.label('id'), creatives.c.is_text.label('is_text'),
                        (creatives.c.weight * creatives.c.parent_weight * text_weight_adjust).label('normalized_weight')],
                       whereclause_zone)
    #for a in model.session.execute(c1).fetchall(): print a
    
    if zone.creative_types == 0: # (Either type)
        # Now that we have our weights in order, let's figure out how many of each thing (text/block) we have, weightwise.
        # This will let us choose texts OR blocks later
        texts_weight = select([func.sum(c1.c.normalized_weight)], c1.c.is_text == True).scalar() or 0
        blocks_weight = select([func.sum(c1.c.normalized_weight)], c1.c.is_text == False).scalar() or 0

        if texts_weight + blocks_weight == 0:
            return _on_empty_zone(zone)
        
        total_weight = texts_weight + blocks_weight
        zone.total_text_weight = texts_weight / total_weight
        
        c1texts = subquery('c1', [c1.c.id, c1.c.normalized_weight], c1.c.is_text == True)
        c1blocks = subquery('c1', [c1.c.id, c1.c.normalized_weight], c1.c.is_text == False)

        _finish_precache(c1texts, texts_weight, zone, True)
        _finish_precache(c1blocks, blocks_weight, zone, False)

    else:    
        # Find total normalized weight of all creatives in order to normalize *that*
        total_weight = select([func.sum(c1.c.normalized_weight)])#.scalar() or 0
        if total_weight == 0:
            return _on_empty_zone(zone)

        _finish_precache(c1, total_weight, zone, zone.creative_types == 1)
    
def _finish_precache(c1, total_weight, zone, is_text):
    
    c2 = c1.alias('c2')

    # Find the total weight above a creative in the table in order to form weighted bins for the random number generator
    # Note that this is the upper bound, not the lower (if it was the lower it could be NULL)
    incremental_weight = select([func.sum(c1.c.normalized_weight) / total_weight], c1.c.id <= c2.c.id, from_obj=c1)
    
    # Get everything into one thing
    # Lower bound = inc_weight - final weight, upper_bound = inc_weight
    shmush = select([c2.c.id,
                     incremental_weight.label('inc_weight'), (c2.c.normalized_weight / total_weight).label('final_weight')],
                    from_obj=c2).alias('shmush')
    #for a in model.session.execute(shmush).fetchall(): print a
    creatives = model.session.execute(shmush).fetchall()
    
    for creative in creatives:
        # current pair?
        pair = model.CreativeZonePair.query.filter_by(zone_id = zone.id, creative_id = creative['id']).first()
        if pair:
            pair.set(dict(is_text = is_text,
                          lower_bound = creative['inc_weight'] - creative['final_weight'],
                          upper_bound = creative['inc_weight']))
        else:
            pair = model.CreativeZonePair(dict(zone_id = zone.id,
                                               creative_id = creative['id'],
                                               is_text = is_text,
                                               lower_bound = creative['inc_weight'] - creative['final_weight'],
                                               upper_bound = creative['inc_weight']))
    
    # Delete old cache objects
    for pair in model.CreativeZonePair.query.filter(and_(model.CreativeZonePair.zone_id == zone.id,
                                                         model.CreativeZonePair.is_text == is_text,
                                                         model.CreativeZonePair.creative_id not in [creative['id'] for creative in creatives])):
        model.session.delete(pair)

    model.session.commit()
    
def _on_empty_zone(zone):
    
    for pair in model.CreativeZonePair.query.filter(model.Zone.id == zone.id):
        model.session.delete(pair)

    model.session.commit()