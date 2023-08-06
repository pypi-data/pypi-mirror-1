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

#from suds import WebFault
from urllib import unquote_plus
from urllib2 import HTTPError
#from suds.sudsobject import asdict

#from adjector.core.cj_util import from_cj_date
from adjector.lib.cj_interface import get_cj_links

from adjector.lib.base import *

log = logging.getLogger(__name__)

class CjController(BaseController):
    
    errors = {}
    
    def start(self):
        if not conf.cj_api_key:
            return 'You must enter an api key in order to connect to Commission Junction.'
        
        # Fill websiteId field
        site_ids = []
        cj_sites = model.Location.query.filter(model.Location.cj_site_id != None)
        if cj_sites:
            site_ids = [[loc.cj_site_id, loc.title] for loc in cj_sites]
        if conf.cj_site_id and conf.cj_site_id not in [str(id) for id, title in site_ids]:
            # if your global site id is yet another thing
            site_ids.insert(0, [conf.cj_site_id, 'Global'])
            
        # Only show the box if neccessary
        if len(site_ids) == 0:
            return 'You must enter at least one global or location-specific site id in order to connect to Commission Junction.'
        elif len(site_ids) == 1:
            c.form = forms.CJLinkSearchOneSite(action='/import/cj/search', value={'website_id': site_ids[0][0]})
        else:
            c.form = forms.CJLinkSearch(action='/import/cj/search', child_args={'website_id': dict(options = site_ids)})

        c.title = 'Import from Commission Junction'
        return render('common.form')

    @rest.dispatch_on(POST='do_search')
    def search(self):
        ''' redo last search'''
        if not session.has_key('last_search'):
            return redirect_to('/import/cj')
        
        last = session['last_search']

        if request.params.has_key('page') and request.params['page'] != last['form_result']['page_number']:
            # render new one, I guess
            self.form_result = last['form_result']
            self.form_result['page_number'] = request.params['page']
            return self._actually_do_search()
        
        c.links = last['links']
        c.total = last['total']
        c.page = last['page']
        c.count = last['count']
        c.per_page = last['per_page']
        
        self._process(c.links, all=True)
        c.title = 'Import from Commission Junction'
        return render('cj.links')

    @rest.restrict('POST')
    @validate(form=forms.CJLinkSearch, error_handler='list')
    def do_search(self):
        return self._actually_do_search()
        
    def _actually_do_search(self):
        
        if not conf.cj_api_key:
            return 'You must enter the necessary credentials in order to connect to Commission Junction.'
        
        result = self.form_result.copy()
        c.show_imported = self.form_result.pop('show_imported')
        c.show_ignored = self.form_result.pop('show_ignored')

        try:
            links, counts = get_cj_links(**self.form_result)
        except HTTPError, error:
            return 'Could not connect to Commission Junction.<br />Code: %s<br />Error: %s' % (error.code, error.msg)
    
        c.total = counts['total']
        c.page = counts['page']
        c.count = counts['count']
        c.per_page = self.form_result['records_per_page']
        
        if c.total == 0:
            return 'No Links Found'
        
        self._process(links)

        session['last_search'] = dict(form_result=result, links=c.links, total=c.total, page=c.page, count=c.count, per_page = c.per_page)
        session.save()

        c.title = 'Import from Commission Junction'
        return render('cj.links')
    
    def _process(self, links, all=False):
        
        session['cj_links'] = session.get('cj_links', {})
        c.links = []
        for link in links:
            # Add to sessionn
            session['cj_links']['%s:%s' % (link['cj_site_id'], link['cj_link_id'])] = link
            
            # Filter more for what to display...

            # Check if ignored.  If so, continue unless paramenter sent.
            link['ignored'] = model.CJIgnoredLink.query.filter_by(cj_link_id = link['cj_link_id']).first()
            if link['ignored'] is not None and not (all or c.show_ignored):
                continue
            
            # Check to see if we already have this imported.  If so, continue unless parameter sent
            link['creative']  = model.Creative.query.filter_by(cj_link_id = link['cj_link_id']).first()
            if link['creative'] is not None and not (all or c.show_imported):
                continue
            
            c.links.append(link)

        session.save()
    
    def process(self):
        ''' Process multiple links at once '''
        
        # See if we still have the links somewhere
        try:
            links = session['cj_links']
        except KeyError:
            session['message'] = 'Link storage error; try searching again before importing any links.'
            session.save()
            return redirect_to('/import/cj')
        
        idents = [unquote_plus(param) for param in request.params.keys() if ':' in unquote_plus(param)]
            
        ### ADD LINKS ###
        if request.params.has_key('import'):
            action, verb = self._add, 'imported'
        
        ### IGNORE LINKS ###
        elif request.params.has_key('ignore'):
            action, verb = self._ignore, 'ignored'

        ## UNIGNORE LINKS ###
        elif request.params.has_key('unignore'):
            action, verb = self._unignore, 'unignored'
        
        else:
            return redirect_to('/import/cj/search')
            
        count = 0
        self.updated = []
        for ident in idents:
            link = links[ident]
            count += action(link)
            
        if action == self._add:
            self._on_updates(self.updated)
        
        session['message'] = '%i links %s.' % (count, verb)
        if count < len(idents):
            session['message'] += '  %i links were already %s.' % (len(idents) - count, verb)

        session.save()
        return redirect_to('/import/cj/search')
    
    def _add(self, link):

        # Do we already have this one as a creative?
        if model.Creative.query.filter_by(cj_link_id = link['cj_link_id']).first() is not None:
            log.warn('Link id %s already added' % link['cj_link_id']) #TODO: output message
            return False

        # Remove ignored tag if neccessary
        ignored = model.CJIgnoredLink.query.filter_by(cj_link_id = link['cj_link_id']).first()
        if ignored:
            model.session.delete(ignored)
        
        # Create set if necessary
        theset = model.Set.query.filter_by(cj_advertiser_id = link['cj_advertiser_id']).first()
        if theset is None:
            theset = model.Set(dict(title = link['advertiser_name'], cj_advertiser_id = link['cj_advertiser_id']))
            self.updated.extend(theset._updated)
        
        # Import link to creative
        creative = model.Creative(dict([key, value] for key, value in link.iteritems() if key in model.Creative.__dict__))
        self.updated.extend(creative._updated)
        creative.parent = theset
        model.session.commit()
        
        return True
            
    def _ignore(self, link):

        ignored = model.CJIgnoredLink.query.filter_by(cj_link_id = link['cj_link_id']).first()
        if ignored:
            log.warn('Tried to ignore a link that was already ignored. Link id = %s' % link['cj_link_id'])
            return False
        model.CJIgnoredLink(link['cj_link_id'], link['cj_advertiser_id'])
        model.session.commit()
        
        return True

    def _unignore(self, link):

        ignored = model.CJIgnoredLink.query.filter_by(cj_link_id = link['cj_link_id']).first()
        if not ignored:
            log.warn('Tried to unignore a link that was not ignored. Link id = %s' % link['cj_link_id'])
            return False
        
        else:                
            model.session.delete(ignored)
            model.session.commit()

        return True