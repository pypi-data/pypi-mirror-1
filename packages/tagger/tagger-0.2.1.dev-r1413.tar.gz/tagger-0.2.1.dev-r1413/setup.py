##########################################################
#
# Licensed under the terms of the GNU Public License
# (see docs/LICENSE.GPL)
#
# Copyright (c) 2006:
#   - The Open Planning Project (http://www.openplans.org/)
#   - Whit Morriss <d.w.morriss@gmail.com>
#   - and contributors
#
##########################################################
from setuptools import setup, find_packages
import sys, os

version= "0.2.1"
    
setup(name='tagger',
      version=version,
      url='http://www.openplans.org/projects/yucca/install-tagger',
      license='GPL',
      description='Tagging Library utilizing rdflib',
      author='Whit Morriss',
      author_email='whit@openplans.org',
      long_description="Provides a wrapper around an rdflib Graph object "
                       "with an api designed for handling basic 'tagging' "
                       "scenarios.",
      download_url="http://www.openplans.org/projects/yucca/install-tagger",
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['tagger'],
      install_requires=['rdflib==2.3.1events',
                        'RuleDispatch',
                        'memojito',
                       ],
      dependency_links=[
                        'http://www.openplans.org/projects/yucca/install-tagger',
                        'http://svn.rdflib.net/branches/michel-events#egg=rdflib-2.3.1events',       
                        'http://peak.telecommunity.com/snapshots/',
                        ],
      zip_safe = True,
      )
