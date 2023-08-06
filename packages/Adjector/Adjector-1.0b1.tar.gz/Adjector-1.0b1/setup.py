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
try:
    from setuptools import setup, find_packages
except ImportError: #Automagically downloads and installs setuptools if you don't have it
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    
import sys
from pkg_resources import require, DistributionNotFound

try:
    require('AdjectorClient')
    print
    print 'You already have AdjectorClient installed.'
    print 'You need to remove AdjectorClient from your site-packages before installing'
    print 'the full version of Adjector, or conflicts may result.'
    print
    sys.exit()
    
except DistributionNotFound:
    pass

setup(
    name='Adjector',
    version='1.0b1',
    description='A lightweight, fast, flexible ad server.  Stays out of your way.',
    long_description='''A lightweight, fast, flexible, open-source ad server.  Serves plain text, HTML, and Javascript ads to your web application in several different ways, even from a separate machine.  Tracks views and clicks.  Designed to save you time and effort and stay out of your way.  Written in Pylons.''',
    author='David Isaacson',
    author_email='david@icapsid.net',
    url='http://projects.icapsid.net/adjector',
    license='GPL v2 or v3 (at your option)',
    install_requires=[
        'Pylons>=0.9.7',
        'SQLAlchemy==0.5.2',
        'Genshi>=0.4',
        'Elixir==0.7.0dev-icapsid-r449',
        #'suds>=0.3.4',
        'ToscaWidgets>=0.9.4',
        'tw.forms>=0.9.1, !=0.9.2',
        'Paste>=1.7.2',
        'PasteDeploy==1.3.3', # Really any newish version of Paste should work,
        'PasteScript==1.7.3', # but if we don't specify one it tries to dl the dev versions from icapsid.
        'pysqlite>=2.0', # Only req'd for sqlite of course : )
        'python-dateutil',
	'pytz', 
    ],
    #setup_requires=["PasteScript>=1.6.3"],
    
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['adjector'],
    
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'adjector': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'adjector': [
    #        ('**.py', 'python', None),
    #        ('public/**', 'ignore', None)]},
    #zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = adjector.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
     
    [paste.filter_app_factory]
    main = adjector.lib.middleware:make_middleware
    
    [paste.filter_factory]
    null = adjector.lib.middleware:null_middleware
    """,
)
