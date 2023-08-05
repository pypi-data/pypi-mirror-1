"""setup - setuptools based setup for hatom2atom

Created and maintained by Luke Arno <luke.arno@gmail.com>

Copyright (C) 2006 Luke Arno <luke.arno@gmail.com> 

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.

Luke Arno can be found at http://lukearno.com/
"""

from setuptools import setup, find_packages
from glob import glob

desc = 'WSGI proxy for transforming hAtom to Atom via hAtom2Atom.xsl.'

setup(name='hatom2atom',
      version='0.3',
      description=desc,
      long_description=desc,
      author='Luke Arno',
      author_email='luke.arno@gmail.com',
      url='http://lukearno.com/projects/hatom2atom',
      license="GPL2",
      install_requires="flup\nkid >= 0.8",
      packages = find_packages(),
      data_files=[('xsl', glob('xsl/*.xsl')), ('kid', glob('kid/*.kid'))],
      entry_points={'console_scripts':['h2aserve = hatom2atom.h2aproxy:run']},
      keywords="xml html micorformats atom hatom wsgi proxy",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Text Processing :: Markup :: XML',
          'Topic :: Text Processing :: Markup :: HTML',])

