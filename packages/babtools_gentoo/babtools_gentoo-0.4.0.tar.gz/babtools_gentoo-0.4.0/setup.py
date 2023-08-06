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

"""Some tools for the casual Gentoo user and ebuild dabbler. 

Info and API: http://rakjar.de/babtools_gentoo/apidocs/ """

from setuptools import setup
from babtools_gentoo import __doc__ as babtools_gentoo__doc__

# Create the desription from the docstrings 

DESCRIPTION = __doc__.split("\n")[0]

LONG_DESCRIPTION = "\n".join(__doc__.split("\n")[1:])

LONG_DESCRIPTION += "\n\n" + babtools_gentoo__doc__

setup(name='babtools_gentoo',
      version='0.4.0',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION, 
      author='Arne Babenhauserheide',
      author_email='arne_bab@web.de',
      keywords=["Gentoo", "local ebuilds", "download and digest ebuilds", "convenience"], 
      license="GNU GPL-3 or later", 
      platforms=["Any Gentoo"], 
      requires = ["portage", "g_pypi"], 
      classifiers = [
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Programming Language :: Python",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Intended Audience :: Developers", 
            "Intended Audience :: End Users/Desktop", 
            "Environment :: Console", 
            "Development Status :: 3 - Alpha"
            ],
      url='http://freehg.org/u/ArneBab/babtools_gentoo',
      #packages = find_packages('.'), 
      #py_modules=['babtools_gentoo'],
      scripts=["babtools_gentoo.py"]
     )
