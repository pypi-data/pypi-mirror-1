#!/usr/bin/env python

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

from pkg_resources import require, DistributionNotFound

# Load the client only unless the full package is already installed
try:
    require('Adjector')
    adjector_required='Adjector' 
except DistributionNotFound:
    adjector_required = 'AdjectorClient'

setup(
    name='AdjectorTracPlugin',
    version='1.0b2',
    packages=find_packages(),
    namespace_packages=['adjector', 'adjector.plugins'],
    author='David Isaacson',
    author_email='david@icapsid.net',
    description='Integrate Adjector into your trac installation: render zones in trac templates.',
    url='http://projects.icapsid.net/adjector',
    license='GPL v2 or v3, at your option',
    #zip_safe=False,
    
    install_requires=[
        '%s>=1.0b2' % adjector_required,
        'trac>=0.10'
    ],
    
    entry_points = {
        'trac.plugins': [
        	'plugin = adjector.plugins.trac'
        ]
    }
)
