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
import random
import re

from sqlalchemy import and_, func, or_
from sqlalchemy.sql import case, join, select, subquery

import adjector.model as model

from adjector.core.conf import conf
from adjector.core.tracking import remove_tracking

log = logging.getLogger(__name__)

def old_render_zone(ident, track=None, admin=False):
    '''
    Render A Random Creative for this Zone.  Access by id or name.
    
    Respect all zone requirements.  Use creative weights and their containing set weights to weight randomness.
    If zone.normalize_by_container, normalize creatives by the total weight of the set they are in, 
    so the total weight of the creatives directly in any set is always 1.
    If block and text ads can be shown, a decision will be made to show one or the other based on the total probability of each type of creative.
    Note that this function is called by the API function render_zone.
    '''
    
    # Note that this is my first time seriously using SA, feel free to clean this up
    if isinstance(ident, int) or ident.isdigit():
        zone = model.Zone.get(int(ident))
    else:
        zone = model.Zone.query.filter_by(name=ident).first()

    if zone is None: # Fail gracefully, don't commit suicide because someone deleted a zone from the ad server
        log.error('Tried to render zone %s.  Zone Not Found' % ident)
        return ''
    
    # Find zone site_id, if applicable.  Default to global site_id, or else None.
    cj_site_id = zone.parent_cj_site_id or conf.cj_site_id
    
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
    
    creative_types = zone.creative_types # This might change later.
    doing_text = None # just so it can't be undefined later
    
    # Sanity check - this shouldn't ever happen
    if zone.num_texts == 0:
        creative_types = 2

    # Filter by text or block if needed.  If you want both we do some magic later.  But first we need to find out how much of each we have, weight wise.
    if creative_types == 1:
        whereclause_zone.append(model.Creative.is_text==True)
        number_needed = zone.num_texts
        doing_text = True
    elif creative_types == 2:
        whereclause_zone.append(model.Creative.is_text==False)
        number_needed = 1
        doing_text = False
    
    
    creatives = model.Creative.table
    
    all_results = []
    
    # Find random creatives; Loop until we have as many as we need
    while True:
    
        # First let's figure how to normalize by how many items will be displayed.  This ensures all items are displayed equally.
        # We want this to be 1 for blocks and num_texts for texts.  Also throw in the zone.weight_texts
        #items_displayed = cast(creatives.c.is_text, Integer) * (zone.num_texts - 1) + 1
        text_weight_adjust = case([(True, zone.weight_texts / zone.num_texts), (False, 1)], creatives.c.is_text)
    
        if zone.normalize_by_container:
            # Find the total weight of each parent in order to normalize
            parent_weights = subquery('parent_weight', 
                                      [creatives.c.parent_id, func.sum(creatives.c.parent_weight * creatives.c.weight).label('pw_total')],
                                      group_by=creatives.c.parent_id)
            
            # Join creatives table and normalized weight table - I'm renaming a lot of fields here to make life easier down the line
            # SA was insisting on doing a full subquery anyways (I just wanted a join)
            c1 = subquery('c1', 
                          [creatives.c.id.label('id'), creatives.c.title.label('title'), creatives.c.html.label('html'),
                           creatives.c.html_tracked.label('html_tracked'), creatives.c.is_text.label('is_text'),
                           creatives.c.cj_site_id.label('cj_site_id'),
                           (creatives.c.weight * creatives.c.parent_weight * text_weight_adjust / 
                                case([(parent_weights.c.pw_total > 0, parent_weights.c.pw_total)], else_ = None)).label('normalized_weight')], # Make sure we can't divide by 0
                           whereclause_zone, # here go our filters
                           from_obj=join(creatives, parent_weights, or_(creatives.c.parent_id == parent_weights.c.parent_id,
                                                                    and_(creatives.c.parent_id == None, parent_weights.c.parent_id == None)))).alias('c1')
    
        else:
            # We don't normalize weight by parent weight, so we dont' need fancy joins
            c1 = subquery('c1', 
                           [creatives.c.id, creatives.c.title, creatives.c.html, creatives.c.html_tracked, creatives.c.is_text, creatives.c.cj_site_id,
                           (creatives.c.weight * creatives.c.parent_weight * text_weight_adjust).label('normalized_weight')],
                           whereclause_zone)
        #for a in model.session.execute(c1).fetchall(): print a
        
        if creative_types == 0: # (Either type)
            # Now that we have our weights in order, let's figure out how many of each thing (text/block) we have, weightwise.
            texts_weight = select([func.sum(c1.c.normalized_weight)], c1.c.is_text == True).scalar() or 0
            blocks_weight = select([func.sum(c1.c.normalized_weight)], c1.c.is_text == False).scalar() or 0
    
            # Create weighted bins, text first (0-whatever).  We are going to decide what kind of thing to make right here, right now,
            # based on the weights of each.  Because we can't have both (yet).
            rand = random.random()
            if texts_weight + blocks_weight == 0:
                break
            if rand < texts_weight / (texts_weight + blocks_weight):
                c1 = c1.select().where(c1.c.is_text == True).alias('text')
                total_weight = texts_weight
                number_needed = zone.num_texts
                doing_text = True
            else:
                c1 = c1.select().where(c1.c.is_text == False).alias('nottext')
                total_weight = blocks_weight
                number_needed = 1
                doing_text = False
            
        else:    
            # Find total normalized weight of all creatives in order to normalize *that*
            total_weight = select([func.sum(c1.c.normalized_weight)])#.scalar() or 0
            #if not total_weight:
            #    break
        
        c2 = c1.alias('c2')
    
        # Find the total weight above a creative in the table in order to form weighted bins for the random number generator
        # Note that this is the upper bound, not the lower (if it was the lower it could be NULL)
        incremental_weight = select([func.sum(c1.c.normalized_weight) / total_weight], c1.c.id <= c2.c.id, from_obj=c1)
        
        # Get everything into one thing - for debugging this is a good place to select and print out stuff
        shmush = select([c2.c.id, c2.c.title, c2.c.html, c2.c.html_tracked, c2.c.cj_site_id,
                         incremental_weight.label('inc_weight'), (c2.c.normalized_weight / total_weight).label('final_weight')],
                        from_obj=c2).alias('shmush')
        #for a in model.session.execute(shmush).fetchall(): print a
        
        # Generate some random numbers and comparisons - sorry about the magic it saves about 10 lines
        # The crazy 0.9999 is to make sure we don't get a number so close to one we run into float precision errors (all the weights might not quite sum to 1,
        # and so we might end up falling outside the bin!)
        # Experimentally the error never seems to be worse than that, and that number is imprecise enough to be displayed exactly by python.
        rand = [random.random() * 0.9999999999 for i in xrange(number_needed)] 
        whereclause_rand = or_(*[and_(shmush.c.inc_weight - shmush.c.final_weight <= rand[i], rand[i] < shmush.c.inc_weight) for i in xrange(number_needed)])
        
        # Select only creatives where the random number falls between its cutoff and the next
        results = model.session.execute(select([shmush.c.id, shmush.c.title, shmush.c.html, shmush.c.html_tracked, shmush.c.cj_site_id], whereclause_rand)).fetchall()
        
        # Deal with number of results
        if len(results) == 0:
            if not doing_text or not all_results:
                return ''
            # Otherwise, we are probably just out of results.
            break

        if len(results) > number_needed:
            log.error('Too many results while rendering zone %i.  I got %i results and wanted %i' % (zone.id, len(results), number_needed))
            results = results[:number_needed]
            all_results.extend(results)
            break
        
        elif len(results) < number_needed:
            if not doing_text:
                raise Exception('Somehow we managed to get past several checks, and we have 0 < results < needed_results for block creatives.' + \
                                 'Since needed_results should be 1, this seems fairly difficult.')
                
            all_results.extend(results)
            # It looks like we need more results, this should only happen when we are doing text.  Try again.
            number_needed -= len(results)
            # Exclude ones we've already got
            whereclause_zone.append(and_(*[model.Creative.id != result.id for result in results]))
            # Set to only render text this time around
            if creative_types == 0:
                creative_types = 1
                whereclause_zone.append(model.Creative.is_text == True)
            # Continue loop...
        
        else: # we have the right number?
            all_results.extend(results)
            break
        
    if doing_text and len(all_results) < zone.num_texts:
        log.warn('Could only retrieve %i of %i desired creatives for zone %i.  This (hopefully) means you are requesting more creatives than exist.' \
                 % (len(all_results), zone.num_texts, zone.id))

    # Ok, that's done, we have our results.
    # Let's render some html
    html = ''
    
    if doing_text:
        html += zone.before_all_text or ''
    
    for creative in all_results:
        if track or (track is None and conf.enable_adjector_view_tracking):
            # Create a view thingy
            model.View(creative['id'], zone.id)
            model.session.commit()

        # Figure out the html value...
        # Use either click tracked or regular html
        if (track or (track is None and conf.enable_adjector_click_tracking)) and creative['html_tracked'] is not None:
            creative_html = creative['html_tracked'].replace('ADJECTOR_TRACKING_BASE_URL', conf.tracking_base_url)\
                .replace('ADJECTOR_CREATIVE_ID', str(creative['id'])).replace('ADJECTOR_ZONE_ID', str(zone.id))
        else:
            creative_html = creative['html']
        
        # Remove or modify third party click tracking
        if (track is False or (track is None and not conf.enable_third_party_tracking)) and creative['cj_site_id'] is not None:
            creative_html = remove_tracking(creative_html, creative['cj_site_id'])
        elif conf.enable_cj_site_replacements:
            creative_html = re.sub(str(creative['cj_site_id']), str(cj_site_id), creative_html)

        ########### Now we can do some text assembly ###########
        # If text, add pre-text
        if doing_text:
            html += zone.before_each_text or ''
            
        html += creative_html

        # Are we in admin mode?
        if admin:
            html += '''
                <div class='adjector_admin' style='color: red; background-color: silver'>
                    Creative: <a href='%(admin_base_url)s%(creative_url)s'>%(creative_title)s</a>
                    Zone: <a href='%(admin_base_url)s%(zone_url)s'>%(zone_title)s</a>
                </div>
                ''' % dict(admin_base_url = conf.admin_base_url, creative_url = '/creative/%i' % creative['id'], zone_url = zone.view(),
                           creative_title = creative.title, zone_title = zone.title)
        
        if doing_text:
            html += zone.after_each_text or ''
            
    if doing_text:
        html += zone.after_all_text or ''
    
    
    # Wrap in javascript if asked
    if html and '<script' not in html and conf.require_javascript:
        wrapper = '''<script type='text/javascript'>document.write('%s')</script>'''
        
        # Do some quick substitutions to inject... #TODO there must be an existing function that does this
        html = re.sub(r"'", r"\'", html) # escape quotes
        html = re.sub(r"[\r\n]", r"", html) # remove line breaks
        return wrapper % html

    return html

def render_zone(ident, track=None, admin=False):
    '''
    Render A Random Creative for this Zone, using precached data.  Access by id or name.
    
    Respect all zone requirements.  Use creative weights and their containing set weights to weight randomness.
    If zone.normalize_by_container, normalize creatives by the total weight of the set they are in, 
    so the total weight of the creatives directly in any set is always 1.
    If block and text ads can be shown, a decision will be made to show one or the other based on the total probability of each type of creative.
    Note that this function is called by the API function render_zone.
    '''
    
    if isinstance(ident, int) or ident.isdigit():
        zone = model.Zone.get(int(ident))
    else:
        zone = model.Zone.query.filter_by(name=ident).first()

    if zone is None: # Fail gracefully, don't commit suicide because someone deleted a zone from the ad server
        log.error('Tried to render zone %s.  Zone Not Found' % ident)
        return ''
    
    # Find zone site_id, if applicable.  Default to global site_id, or else None.
    cj_site_id = zone.parent_cj_site_id or conf.cj_site_id
    
    # Texts or blocks?
    rand = random.random()
    if rand < zone.total_text_weight:
        # texts!
        number_needed = zone.num_texts
        doing_text = True
    else:
        # blocks!
        number_needed = 1
        doing_text = False
        
    query = model.CreativeZonePair.query.filter_by(zone_id = zone.id, is_text = doing_text)
    num_pairs = query.count()
    if num_pairs == number_needed:
        pairs = query.all()
    
    else:
        pairs = [] # keep going until we get as many as we need
        still_needed = number_needed
        banned_ranges = []
        while still_needed:
            # Generate some random numbers and comparisons - sorry about the magic it saves about 10 lines
            # The crazy 0.9999 is to make sure we don't get a number so close to one we run into float precision errors (all the weights might not quite sum to 1,
            # and so we might end up falling outside the bin!)
            # Experimentally the error never seems to be worse than that, and that number is imprecise enough to be displayed exactly by python.
    
	    rand_clauses = []
            loop_counter = 0
            while len(rand_clauses) < still_needed:
                rand = random.random() * 0.9999999999
                if not any(range[0] <= rand < range[1] for range in banned_ranges):
                    rand_clauses.append(and_(model.CreativeZonePair.lower_bound <= rand, rand < model.CreativeZonePair.upper_bound))
              
                loop_counter += 1
                if loop_counter > 1000:
		    log.error('Not able to find a reasonable random number for zone %i' % zone.id)
                    break

            results = query.filter(or_(*rand_clauses)).all()
            
            # What if there are no results?
            if len(results) == 0:
                if not pairs: # I guess there are no results
                    return ''
                break # or else we are just out of results
            
            still_needed -= len(results)
            pairs += results
            
            # Exclude ones we've already got, if we need to loop again
            banned_ranges.extend([pair.lower_bound, pair.upper_bound] for pair in results)

        #JIC
        if len(pairs) > number_needed:
            # This shouldn't be able to happen
            log.error('Too many results while rendering zone %i.  I got %i results and wanted %i' % (zone.id, len(results), number_needed))
            pairs = pairs[:number_needed]
            
        elif len(pairs) < number_needed:
            log.warn('Could only retrieve %i of %i desired creatives for zone %i.  This (hopefully) means you are requesting more creatives than exist.' \
                     % (len(pairs), zone.num_texts, zone.id))

    # Ok, that's done, we have our results.
    # Let's render some html
    html = ''
    
    if doing_text:
        html += zone.before_all_text or ''
    
    for pair in pairs:
        creative = pair.creative
        
        if track or (track is None and conf.enable_adjector_view_tracking):
            # Create a view thingy - this is much faster than using SA (almost instant)
            model.session.execute('INSERT INTO views (creative_id, zone_id, time) VALUES (%i, %i, now())' % (creative.id, zone.id))
            #model.View(creative.id, zone.id)

        # Figure out the html value...
        # Use either click tracked or regular html
        if (track or (track is None and conf.enable_adjector_click_tracking)) and creative.html_tracked is not None:
            creative_html = creative.html_tracked.replace('ADJECTOR_TRACKING_BASE_URL', conf.tracking_base_url)\
                .replace('ADJECTOR_CREATIVE_ID', str(creative.id)).replace('ADJECTOR_ZONE_ID', str(zone.id))
        else:
            creative_html = creative.html
        
        # Remove or modify third party click tracking
        if (track is False or (track is None and not conf.enable_third_party_tracking)) and creative.cj_site_id is not None:
            creative_html = remove_tracking(creative_html, creative.cj_site_id)
        elif cj_site_id and creative.cj_site_id and conf.enable_cj_site_replacements:
            creative_html = re.sub(str(creative.cj_site_id), str(cj_site_id), creative_html)

        ########### Now we can do some text assembly ###########
        # If text, add pre-text
        if doing_text:
            html += zone.before_each_text or ''
            
        html += creative_html

        # Are we in admin mode?
        if admin:
            html += '''
                <div class='adjector_admin' style='color: red; background-color: silver'>
                    Creative: <a href='%(admin_base_url)s%(creative_url)s'>%(creative_title)s</a>
                    Zone: <a href='%(admin_base_url)s%(zone_url)s'>%(zone_title)s</a>
                </div>
                ''' % dict(admin_base_url = conf.admin_base_url, creative_url = '/creative/%i' % creative.id, zone_url = zone.view(),
                           creative_title = creative.title, zone_title = zone.title)
        
        if doing_text:
            html += zone.after_each_text or ''
            
    if doing_text:
        html += zone.after_all_text or ''
    
    model.session.commit() #having this down here saves us quite a bit of time

    # Wrap in javascript if asked
    if html and '<script' not in html and conf.require_javascript:
        wrapper = '''<script type='text/javascript'>document.write('%s')</script>'''
        
        # Do some quick substitutions to inject... #TODO there must be an existing function that does this
        html = re.sub(r"'", r"\'", html) # escape quotes
        html = re.sub(r"[\r\n]", r"", html) # remove line breaks
        return wrapper % html

    return html
