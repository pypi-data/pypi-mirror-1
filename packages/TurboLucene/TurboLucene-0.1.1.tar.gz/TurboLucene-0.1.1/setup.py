#!/usr/bin/env python2.4
#==============================================================================
#
# Copyright (c) 2007 Krys Wilken
#
# This software is licensed under the MIT license.  See the LICENSE file for
# licensing information.
#
#==============================================================================

"""TurboLucene's setup script.

Type python setup.py install to install TurboLucene.

"""


#---Third-Party imports

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages


#---Globals

__revision__ = '$Id: setup.py 17 2007-01-31 07:13:08Z krys $'


#---Main

readme_file = open('README')
long_description = readme_file.read()
readme_file.close()

setup(
  name='TurboLucene',
  version='0.1.1',
  install_requires=['TurboGears>=1.0'],
  py_modules=['turbolucene'],
  include_package_data=True,
  author='Krys Wilken',
  author_email='krys@krys.ca',
  license='MIT',
  description='TurboLucene is a library that allows TurboGears applications \
to easily use the PyLucene full text search engine.',
  long_description=long_description,
  url='http://dev.krys.ca/turbolucene',
  download_url='http://dev.krys.ca/turbolucene',
  keywords='turbolucene turbogears pylucene full text search engine',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: TurboGears',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
    'Topic :: Software Development :: Libraries :: Python Modules'])
