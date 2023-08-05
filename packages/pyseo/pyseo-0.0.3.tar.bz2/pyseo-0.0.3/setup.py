#!/usr/bin/env python
"""
pyseo package version 0.01
Setup Script (distutils)

Copyright (c) 2007 GreenMice Solutions [http://greenmice.info]
Copyright (c) 2007 Vladimir Rusinov <vladimir@greenmice.info>

pyseo is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

pyseo is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
Infobiller; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
Fifth Floor, Boston, MA  02110-1301  USA
"""

from distutils.core import setup
setup(name='pyseo',
      version='0.0.3',
      description='Set of python modules for SEO masters',
      author='Vladimir Rusinov',
      author_email='vladimir@greenmice.info',
      #url='http://not-yet-available/,
      #package_dir = {'': 'pyseo'},
      packages=['pyseo',
        'pyseo.poschecker'
        ],
        
        long_description="""
            pyseo is a set of modules to be used in SEO soft.
        
            Now, in this pre-alfa, pyseo includes only one userful module:
            pyseo.poschecker.yandex is a site positiong checker for yandex.ru
        """,
        classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Python Software Foundation License',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          #'Topic :: SEO',
          #'Topic :: Business'
        ],
        requires=[
            'BeautifulSoup'
          ],
        license="GPL-3"
     )
