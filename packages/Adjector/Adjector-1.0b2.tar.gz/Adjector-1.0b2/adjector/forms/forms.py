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

import tw.api as twa
import tw.forms as twf

from formencode.schema import Schema
from tw.forms.validators import Int, Number, UnicodeString

from adjector.core.conf import conf
import adjector.model as model

from adjector.forms.validators import *

class FilteringSchema(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    
class GenericField(twf.FormField):
    template = 'genshi:adjector.templates.form.widgets.generic_field'

# Some shortcuts
UnicodeEmptyString = UnicodeString(strip=True, not_empty=False, if_missing=None)
UnicodeNonEmptyString = UnicodeString(strip=True, not_empty=True, max=80)
IntMissing = Int(if_missing=None)
PositiveInt = Int(min=0, if_missing=None)

class CreativeForm(twf.ListForm):
    '''Creative creation form'''
    
    class fields(twa.WidgetsList):
        preview = GenericField(label_text='Preview', validator=None, edit_only=True)

        title = twf.TextField(label_text='Title', validator=UnicodeNonEmptyString, size=50)
        
        parent_id = twf.SingleSelectField(label_text='Set', validator=Int)

        is_text = twf.SingleSelectField(label_text='Type', options=[[0, 'Block'], [1, 'Text']], 
                                        validator=AsBool(not_empty=True))
        
        weight = twf.TextField(label_text='Weight', default=1.0, validator=Number(not_empty=True, min=0.0))
        total_weight = twf.TextField(label_text='Total Weight', validator=None, disabled=True, edit_only=True)
        

        html = twf.TextArea(label_text='HTML', cols=100, rows=10, 
                            validator=UnicodeString(strip=True, not_empty=False, if_missing=''))
        
        html_tracked = twf.TextArea(label_text='HTML with Tracking Code', cols=100, rows=10, validator=None, disabled=True, edit_only=True)
        
        add_tracking = twf.CheckBox(label_text='Add Tracking', 
                                    help_text='Won\'t be used unless enable_adjector_click_tracking is true.', 
                                    default=True)
        
        width = twf.TextField(label_text='Width', validator=PositiveInt)
        
        height = twf.TextField(label_text='Height', validator=PositiveInt)
        
        start_date = twf.TextField(label_text='Start Date', validator=DateTime(if_missing=None))
        
        end_date = twf.TextField(label_text='End Date', validator=DateTime(end_interval=True, if_missing=None))
        
        disabled = twf.CheckBox(label_text='Disabled', default=False)
    
        delete = twf.SubmitButton(default='Delete', named_button=True, validator=None, edit_only=True)
        
    validator = FilteringSchema()
    template = 'genshi:adjector.templates.form.basic'

Creative = CreativeForm('new_creative')

class LocationForm(twf.ListForm):
    '''Set creation form'''
    
    class fields(twa.WidgetsList):
        title = twf.TextField(label_text='Title', validator=UnicodeNonEmptyString, size=50)
        parent_id = twf.SingleSelectField(label_text='Parent Location', validator=Int)
        description = twf.TextArea(label_text='Description', cols=100, rows=5, validator=UnicodeEmptyString)
        cj_site_id = twf.TextField(label_text='CJ Site ID', validator=Int(min=0))
        delete = twf.SubmitButton(default='Delete', named_button=True, validator=None, edit_only=True)

    validator = FilteringSchema()
    template = 'genshi:adjector.templates.form.basic'

Location = LocationForm()

class SetForm(twf.ListForm):
    '''Set creation form'''
    
    class fields(twa.WidgetsList):
        title = twf.TextField(label_text='Title', validator=UnicodeNonEmptyString, size=50)
        parent_id = twf.SingleSelectField(label_text='Parent Set', validator=Int)
        weight = twf.TextField(label_text='Weight', default=1.0, validator=Number(not_empty=True, min=0.0))
        total_weight = twf.TextField(label_text='Total Weight', validator=None, disabled=True, edit_only=True)
        description = twf.TextArea(label_text='Description', cols=100, rows=5, validator=UnicodeEmptyString)
        delete = twf.SubmitButton(default='Delete', named_button=True, validator=None, edit_only=True)

    validator = FilteringSchema()
    template = 'genshi:adjector.templates.form.basic'

Set = SetForm()

class ZoneForm(twf.ListForm):
    '''Zone creation form'''
    
    class fields(twa.WidgetsList):
        preview = GenericField(label_text='Preview', validator=None, edit_only=True)
        title = twf.TextField(label_text='Title', validator=UnicodeNonEmptyString, size=50)
        name = twf.TextField(label_text='Unique Name', help_text='optional; an alternate way to access the zone',
                              validator = SimpleString(strip=True, not_empty=False, max=80))
        parent_id = twf.SingleSelectField(label_text='Location', validator=Int, help_text='necessary for imported creatives to display here')
        creative_types = twf.SingleSelectField(label_text='Show Creative Types', options=[[0, 'Blocks and Text'], [1, 'Text Only'], [2, 'Blocks Only']], 
                                               validator=Int(not_empty=True, min=0, max=2))
        description = twf.TextArea(label_text='Description', cols=100, rows=5, validator=UnicodeEmptyString)

        min_width = twf.TextField(label_text='Min Width', validator=PositiveInt)
        max_width = twf.TextField(label_text='Max Width', validator=PositiveInt)
        min_height = twf.TextField(label_text='Min Height', validator=PositiveInt)
        max_height = twf.TextField(label_text='Max Height', validator=PositiveInt)
        
        num_texts = twf.TextField(label_text='Number of Text Creatives to Show', default=1, validator=Int(not_empty=False, min=1, if_missing=1))
        before_all_text = twf.TextArea(label_text='Before All Text Creatives', validator=UnicodeEmptyString, cols=100)
        after_all_text = twf.TextArea(label_text='After All Text Creatives', validator=UnicodeEmptyString, cols=100)
        before_each_text = twf.TextArea(label_text='Before Each Text Creative', validator=UnicodeEmptyString, cols=100)
        after_each_text = twf.TextArea(label_text='After Each Text Creative', validator=UnicodeEmptyString, cols=100)
        weight_texts = twf.TextField(label_text='Adjust Weight for Text Creatives (Blocks = 1.0)', 
                                     default=1.0, validator=Number(not_empty=True, min=0.0, if_missing=1.0))

        normalize_by_container = twf.CheckBox(label_text='Normalize By Container')
        
        previous_name = twf.HiddenField(validator=UnicodeString(strip=True, not_empty=False, max=80, if_missing=None))

        delete = twf.SubmitButton(default='Delete', named_button=True, validator=None, edit_only=True)
    
    validator = FilteringSchema(chained_validators=[
        UniqueValue(lambda name: model.Zone.query.filter_by(name=name).count() == 0, 'name', 'previous_name', not_empty=False)
    ])
    template = 'genshi:adjector.templates.form.basic'
        
Zone = ZoneForm('new_zone')

class CJLinkSearchFields(twa.WidgetsList):
    # Some of these don't seem to be supported by the REST interface.  Thanks CJ, I really appreciate it.
    
    keywords = twf.TextField(label_text='Keywords', help_text = 'space separated, +keyword requires a keyword, -is a not, default is or operation',
                             validator = UnicodeString(strip=True, not_empty=False))
    
#    link_size = twf.SingleSelectField(label_text='Size', validator = UnicodeString(strip=True, not_empty=False),
#                             options=['', '88x31 Micro Bar', '120x60 Button 2', '120x90 Button 1',  
#                                      '150x50 Banner', '234x60 Half Banner', '468x60 Full Banner', '125x125 Square Button', '180x150 Rectangle',
#                                      '250x250 Square Pop-Up', '300x250 Medium Rectangle',  '336x280 Large Rectangle', '240x400 Vertical Rectangle', 
#                                      '120x240 Vertical Banner', '120x600 Skyscraper', '160x600 Wide Skyscraper', 'Other'])

    link_type = twf.SingleSelectField(label_text='Type', validator = UnicodeString(strip=True, not_empty=False),
                                      options=['', 'Banner', 'Advanced Link', 'Text Link', 'Content Link', 'SmartLink',
                                               'Product Catalog', 'Advertiser SmartZone', 'Keyword Link'])

    promotion_start_date = twf.TextField(label_text='Start Date', help_text = 'Format: MM/DD/YYYY',
                                       validator = UnicodeString(strip=True, not_empty=False))
    
    promotion_end_date = twf.TextField(label_text='End Date', help_text = 'Format: MM/DD/YYYY or "Ongoing" for only links with no end date',
                                     validator = UnicodeString(strip=True, not_empty=False))
    
    promotion_type = twf.SingleSelectField(label_text='Promotion Type', help_text = 'Required if Start or End date given',
                                          validator = UnicodeString(strip=True, not_empty=False),
                                          options = ['',
                                                     ['coupon', 'Coupon'],
                                                     ['sweepstakes', 'Sweepstakes'],
                                                     ['product', 'Product'],
                                                     ['sale', 'Sale'],
                                                     ['free shipping', 'Free Shipping'],
                                                     ['seasonal link', 'Seasonal Link']])

#    language = twf.TextField(label_text='Language', default='en', validator = UnicodeString(strip=True, not_empty=False))
    
#    serviceable_area = twf.TextField(label_text='Serviceable Area', default='US', validator = UnicodeString(strip=True, not_empty=False))

    records_per_page = twf.TextField(label_text='Records Per Page', default=100, validator=Int(min=0, not_empty=False))
    page_number = twf.TextField(label_text='Page Number', default=1, validator=Int(min=0, not_empty=False))

#    sort_by = twf.SingleSelectField(label_text='Sort By',
#                                   validator = UnicodeString(strip=True, not_empty=False),
#                                   options=[['', 'Relevance'],
#                                            ['link-id', 'Link ID'], 
#                                            ['link-destination', 'Link Destination'],
#                                            ['link-type', 'Link Type'], 
#                                            ['advertiser-id', 'Advertiser ID'],
#                                            ['advertiser-name', 'Advertiser Name'], 
#                                            ['creative-width', 'Width'],
#                                            ['creative-height', 'Height'],
#                                            ['promotion-start-date', 'Start Date'],
#                                            ['promotion-end-date', 'End Date'],
#                                            ['category', 'Category']])

#    sort_order = twf.SingleSelectField(label_text='Sort Order', options=[['dec', 'Descending'], ['asc', 'Ascending']], 
#                                       validator=UnicodeString(not_empty=True))
    
    show_ignored = twf.CheckBox(label_text='Show Ignored Links')
    show_imported = twf.CheckBox(label_text='Show Imported Links')

class CJLinkSearchForm(twf.ListForm):
    class extra_field(twa.WidgetsList):
        website_id = twf.SingleSelectField(label_text='Website', help_text='Doesn\'t matter much if enable_cj_site_replacements is true.', 
                                          validator=UnicodeString(not_empty=True))
    fields = CJLinkSearchFields + extra_field
    template = 'genshi:adjector.templates.form.basic'

CJLinkSearch = CJLinkSearchForm()

class CJLinkSearchOneSiteForm(twf.ListForm):
    class extra_field(twa.WidgetsList):
        website_id = twf.HiddenField(validator=UnicodeString(not_empty=True))
    fields = CJLinkSearchFields + extra_field
    template = 'genshi:adjector.templates.form.basic'

CJLinkSearchOneSite = CJLinkSearchOneSiteForm()


