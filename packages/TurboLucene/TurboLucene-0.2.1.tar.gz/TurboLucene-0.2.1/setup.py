#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

#==============================================================================
#
# Copyright (c) 2007 Krys Wilken
#
# This is part of the TurboLucene project (http://dev.krys.ca/turbolucene/).
#
# Copyright (c) 2007 Krys Wilken <krys AT krys DOT ca>
#
# This software is licensed under the MIT license.  See the LICENSE file for
# licensing information.
#
#==============================================================================

"""TurboLucene's setup script.

See the README file for installation details.

:Requires: setuptools_

.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools

:newfield revision: Revision

"""

__revision__ = '$Id: setup.py 47 2007-04-01 22:36:05Z krys $'


#---Imports--------------------------------------------------------------------

#---Standard Library imports
from codecs import BOM

#---Third-Party imports
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

#---Project imports
import turbolucene


#---Main-----------------------------------------------------------------------

readme_file = open(u'README')
long_description = readme_file.read()
readme_file.close()
if long_description.startswith(BOM):
    long_description = long_description.lstrip(BOM)
long_description.decode('utf-8')

setup(
  name=u'TurboLucene',
  version=turbolucene.__version__,
  author=turbolucene.__author__,
  author_email=turbolucene.__contact__,
  license=turbolucene.__license__,
  description=(
    u'TurboLucene is a TurboGears extension that allows applications to easily'
    u' use the PyLucene full-text search engine.'
  ),
  long_description=long_description,
  url='http://dev.krys.ca/turbolucene',
  download_url='http://dev.krys.ca/downloads/turbolucene',
  packages=find_packages(exclude=[
    'ez_setup',
  ]),
  include_package_data=True,
  install_requires=[
    'TurboGears>=1.0',
  ],
  keywords=(
    'turbolucene turbogears pylucene full text search engine '
    'turbogears.extension'
  ),
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: TurboGears',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Natural Language :: Czech',
    'Natural Language :: Danish',
    'Natural Language :: German',
    'Natural Language :: Greek',
    'Natural Language :: English',
    'Natural Language :: Spanish',
    'Natural Language :: Finnish',
    'Natural Language :: French',
    'Natural Language :: Italian',
    'Natural Language :: Japanese',
    'Natural Language :: Korean',
    'Natural Language :: Dutch',
    'Natural Language :: Norwegian',
    'Natural Language :: Portuguese',
    'Natural Language :: Portuguese (Brazilian)',
    'Natural Language :: Russian',
    'Natural Language :: Swedish',
    'Natural Language :: Chinese (Simplified)',
  ],
)
