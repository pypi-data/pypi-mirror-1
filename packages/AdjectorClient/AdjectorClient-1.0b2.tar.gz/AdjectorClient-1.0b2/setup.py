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

try:
    from setuptools import setup, find_packages
except ImportError: #Automagically downloads and installs setuptools if you don't have it
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys
from pkg_resources import require, DistributionNotFound

try:
    require('Adjector')
    print
    print 'You already have the full Adjector package installed.'
    print 'You are attempting to install a stripped-down version of Adjector;'
    print 'NO EXTRA FUNCTIONALITY will be provided that you do not already have.'
    print 'However if you are sure you want to do this, you need to remove Adjector'
    print 'from your site-packages directory first. '
    print
    sys.exit()

except DistributionNotFound:
    pass

setup(
    name='AdjectorClient',
        # It would be better to call this something else, but then we might see conflicts (don't want both installed)
    version='1.0b2',
    description='Client-only package for Adjector, a lightweight, fast, flexible ad server.',
    long_description='''This is the client-only package for Adjector.  This package should be used if you would like to render the ads directly from your application, instead of through the server.\n\n Adjector is a lightweight, fast, flexible, open-source ad server.  It serves plain text, HTML, and Javascript ads to your web application in several different ways, even from a separate machine.  It tracks views and clicks.  It is designed to save you time and effort and stay out of your way.  Written in Pylons.''',
    author='David Isaacson',
    author_email='david@icapsid.net',
    url='http://projects.icapsid.net/adjector',
    license='GPL v2 or v3 (at your option)',
    install_requires=[
        'SQLAlchemy>=0.5',
        'Elixir>=0.6.1',
        'pytz',
        'pysqlite>=2.0' # Only req'd for sqlite of course : )
    ],
    
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['adjector'],
    
    #include_package_data=True,
    #test_suite='nose.collector',
    #package_data={'adjector': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'adjector': [
    #        ('**.py', 'python', None),
    #        ('public/**', 'ignore', None)]},
    #zip_safe=False,
)
