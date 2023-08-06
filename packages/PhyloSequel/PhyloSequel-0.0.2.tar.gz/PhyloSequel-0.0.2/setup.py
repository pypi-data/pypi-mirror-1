#! /usr/bin/env python

###############################################################################
##  setup.py
##
##  Part of the PhyloSequel BioSQL database toolkit.
##
##  Copyright 2009 Jeet Sukumaran.
##
##  This program is free software; you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation; either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License along
##  with this program. If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################

"""
Package setup and installation.
"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
from setuptools import find_packages
from phylosequel import PACKAGE_VERSION as PHYLOSEQUEL_VERSION

script_names = ['phylosql-gettree.py', 
                'phylosql-insert.py']

setup(name='PhyloSequel',
      version=PHYLOSEQUEL_VERSION,     
      author='Jeet Sukumaran',
      author_email='jeetsukumaran@gmail.com',
      url='http://jeetworks.org/',
      description="""Toolkit and library for BioSQL database interaction and operations.""",
      license='LGPL 3+',
      packages=['phylosequel'],
      package_dir={'phylosequel': 'phylosequel'},
      package_data={
        "" : ['doc/*'],
        "phylosequel" : ["tests/data/*"]
      },
      scripts = [('scripts/%s' % i) for i in script_names],  
      test_suite = "phylosequel.tests",
      include_package_data=True,         
      zip_safe=True,
      install_requires=[
          "DendroPy >= 2.3.0",
          "SQLAlchemy >= 0.5.2",
      ],    
      long_description="""\
Simple wrappers to facilitate the import and export of phylogenetic data
to and from files and a BioSQL database,""",
      classifiers = [
"Environment :: Console",
"Intended Audience :: Developers",
"Intended Audience :: Science/Research",
"License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
"Natural Language :: English",
"Operating System :: OS Independent",
"Programming Language :: Python",
"Topic :: Scientific/Engineering :: Bio-Informatics",
"Topic :: Database :: Front-Ends"
      ],
      keywords='phylogenetics evolution biology SQL database',      
      )
