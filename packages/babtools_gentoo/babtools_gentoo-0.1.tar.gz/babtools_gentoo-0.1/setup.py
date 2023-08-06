#!/usr/bin/env python
# encoding: utf-8

#    Copyright © 2008 Arne Babenhauserheide
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

"""Some tools for the casual Gentoo user and ebuild dabbler."""

from distutils.core import setup

setup(name='babtools_gentoo',
      version='0.1',
      description=__doc__,
      author='Arne Babenhauserheide',
      author_email='arne_bab@web.de',
      keywords=["Gentoo", "ebuilds"], 
      license="GNU GPL-3 or later", 
      platform=["any gentoo"], 
      url='http://freehg.org/u/ArneBab/babtools_gentoo',
      py_modules=['babtools_gentoo'],
      scripts=["babtools_gentoo.py"]
     )
