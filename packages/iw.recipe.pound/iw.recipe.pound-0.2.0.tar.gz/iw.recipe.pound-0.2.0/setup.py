# -*- coding: utf-8 -*-
# Copyright (C)2007 'Ingeniweb'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
This module contains the tool of iw.recipe.pound
"""
import os
from setuptools import setup, find_packages

version = '0.2.0'

README = os.path.join(os.path.dirname(__file__),
		      'iw',
		      'recipe',
		      'pound', 'docs', 'README.txt')

long_description = open(README).read() + '\n\n'

entry_point = 'iw.recipe.pound:Recipe'

entry_points = {"zc.buildout": ["default = %s" % entry_point]}

setup(name='iw.recipe.pound',
      version=version,
      description="Recipe to install and configure Pound",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='pound zope plone recipe',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='https://ingeniweb.svn.sourceforge.net/svnroot/ingeniweb/iw.recipe.pound',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iw.recipe'],
      include_package_data=True,
      extras_require = dict(test=['zope.testing']),
      zip_safe=False,
      install_requires=[
          'setuptools',
	      'zc.buildout',
	      # -*- Extra requirements: -*-
          'zc.recipe.cmmi'
      ],
      entry_points=entry_points,
      )
