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
''' 
Search Links in the Commission Junction API 

For detailed help, visit http://help.cj.com/en/web_services/Link_Search_Service_v.2.htm
Last updated 2009-04-17

Options:
    advertiserIds: 'joined', 'notjoined' or '', or a comma-separated list of advertiser ids
    keywords: space separated, +keyword requires a keyword, -is a not, default is or operation
    category
    linkType: one of Banner, Advanced Link, Text Link, Content Link, SmartLink, Product Catalog, Advertiser SmartZone, Keyword Link
    linkSize: one of 88x31 Micro Bar, 120x60 Button 2, 120x240 Vertical Banner, 120x90 Button 1, 125x125 Square Button,
        234x60 Half Banner, 468x60 Full Banner, 300x250 Medium Rectangle, 250x250 Square Pop-Up, 240x400 Vertical Rectangle,
        336x280 Large Rectangle, 180x150 Rectangle, 160x600 Wide Skyscraper, 120x600 Skyscraper, 150x50 Banner, Other
    language: a language code
    serviceableArea: a country code
    promotionType: one of coupon, sweepstakes, product, sale, free shipping, seasonal link.
        Required if promotionStartDate and promotionEndDate given.
    *promotionStartDate and *promotionEndDate: MM/DD/YYYY format, promotionEndDate = Ongoing is no end date. 
        If you specify one you must the other and promotionType
        This will actually find ads that run fully any time during this period, not necc. these exact dates.
    sortBy: one of linkId, advertiserName, linkDestination, linkType, creativeWidth, creativeHeight,
        advertiserId, promotionStartDate, promotionEndDate
    sortOrder: asc/desc, defaults to desc
    startAt and maxResults: offset and limit, max results allowed = 100, defaults to 10
    
    * Different name than published API as of last check
'''

#import os.path

#from suds.client import Client
#from libxml2 import parseDoc
from xml.dom.minidom import parseString
from urllib import urlencode
from urllib2 import urlopen, Request

import adjector.model as model

from adjector.core.conf import conf
from adjector.core.cj_util import from_cj_date

#def get_link_search_client():
#    cj_linksearch_wsdl = os.path.join(conf.root, 'external', 'CJ_LinkSearchServiceV2.0.wsdl')
#    return Client('file://' + cj_linksearch_wsdl)
#
#def get_link_search_defaults():
#    return dict(developerKey = conf.cj_api_key,
#                advertiserIds = 'joined',
#                language = 'en',
#                #linkSize = '300x250 Medium Rectangle',
#                serviceableArea = 'US',
#                #promotionEndDate = 'Ongoing',
#                #sortBy = 'linkType',
#                sortOrder = 'desc',
#                startAt = 0,
#                maxResults = 100) #Note: change this for debugging so you don't hammer CJ

def get_link_property(link, property):
    child = link.getElementsByTagName(property)[0].firstChild
    if not child:
        return ''
    return str(child.toxml())

def get_cj_links(**kwargs):
    
    params = {}
    
    for k,v in kwargs.iteritems():
        params[k.replace('_','-')] = v

    params.update({'advertiser-ids': 'joined'})
    
    req = Request('https://linksearch.api.cj.com/v2/link-search?%s' % urlencode(params), 
                  headers = {'authorization': conf.cj_api_key})
    result = urlopen(req).read()
    
    doc = parseString(result)
    links_attr = doc.getElementsByTagName('links')[0]
    
    total = int(links_attr.getAttribute('total-matched'))
    count = int(links_attr.getAttribute('records-returned'))
    page = int(links_attr.getAttribute('page-number'))
    
    links = []
    now = model.tz_now()
    for link in doc.getElementsByTagName('link'):
        
        if get_link_property(link, 'relationship-status') != 'joined':
            # There is no need to show links from advertisers we won't make $$ from
            continue
        if get_link_property(link, 'promotion-end-date') and from_cj_date(get_link_property(link, 'promotion-end-date')) < now:
            # Don't show expired links
            continue
        
        links.append(dict(
            title = get_link_property(link, 'link-name'),
            html = get_link_property(link, 'link-code-html').replace('&lt;', '<').replace('&gt;', '>'),
            is_text = get_link_property(link, 'link-type') == 'Text Link',
            width = int(get_link_property(link, 'creative-width')),
            height = int(get_link_property(link, 'creative-height')),
            start_date = from_cj_date(get_link_property(link, 'promotion-start-date')),
            end_date = from_cj_date(get_link_property(link, 'promotion-end-date')),
            cj_link_id = int(get_link_property(link, 'link-id')),
            cj_advertiser_id = int(get_link_property(link, 'advertiser-id')),
            cj_site_id = int(params['website-id']),
            
            # Values not stored by adjector
            description = get_link_property(link, 'description'),
            link_type = get_link_property(link, 'link-type'),
            advertiser_name = get_link_property(link, 'advertiser-name'),
            promo_type = get_link_property(link, 'promotion-type'),
            seven_day_epc = get_link_property(link, 'seven-day-epc'),
            three_month_epc = get_link_property(link, 'three-month-epc'),
            click_commission = get_link_property(link, 'click-commission'),
            lead_commission = get_link_property(link, 'lead-commission'),
            sale_commission = get_link_property(link, 'sale-commission'),
        ))

    return links, {'count': count, 'total': total, 'page': page}