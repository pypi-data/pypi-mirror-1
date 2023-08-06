# -*- coding: utf-8 -*-
#-##########################################################################-#
#
# xooof - http://www.xooof.org
# A development and XML specification framework for documenting and
# developing the services layer of enterprise business applications.
# From the specifications, it generates WSDL, DocBook, client-side and
# server-side code for Java, C# and Python.
#
# Copyright (C) 2006 Software AG Belgium
#
# This file is part of xooof.
#
# xooof is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# xooof is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#-##########################################################################-#
from setuptools import setup, find_packages
import os

version = '0.1.1'

setup(name='xooof.schema.dev',
      version=version,
      description="The zope schema parts of the xooof runtime development" \
      " tools for python",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Laurent Mignon',
      author_email='laurent.mignon__at__softwareag.com',
      url='http://sourceforge.net/projects/xooof/',
      license='GNU Lesser General Public License',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['xooof', 'xooof.schema'],
      include_package_data=True,
      zip_safe=False,
      dependency_links = [
      ],
      install_requires=[
          'setuptools',
          'xooof.spectools',
          'i18ndude >=3.0b4, <4',
      ],
      entry_points= {
          'console_scripts':
             ['struct2zschema = xooof.schema.dev.structtozschema:main',
              'struct2po = xooof.schema.dev.structtopo:main']},
      )
