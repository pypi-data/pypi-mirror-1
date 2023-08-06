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

"""babtools_EXAMPLE - Example structure with efficient PyPI usage for  babtools.

This example covers a nice setup.py file, which gets name and description for the PyPI from the docstrings in itself as well as in the main file (babtools_EXAMPLE.py). 

The changelog is automatically extracted from the file Changelog.txt and appended to the long description for the PyPI. 

Info and API: http://rakjar.de/babtools_gentoo/apidocs/ """

from setuptools import setup
from babtools_EXAMPLE import __doc__ as babtools__doc__
from babtools_EXAMPLE import __version__, __changelog__

# Create the desription from the docstrings 

DESCRIPTION = __doc__.split("\n")[0].split(" - ")[1:]

LONG_DESCRIPTION = "\n".join(__doc__.split("\n")[1:])

LONG_DESCRIPTION += "\n\n" + babtools__doc__ 

LONG_DESCRIPTION += "\n\n" + __changelog__

setup(name=__doc__.split("\n")[0].split(" - ")[0],
      version=__version__,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION, 
      author='Arne Babenhauserheide',
      author_email='arne_bab@web.de',
      keywords=["babtools"], 
      license="GNU GPL-3 or later", 
      platforms=["any"], 
      requires = ["tagpy"], 
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
      url='http://freehg.org/u/ArneBab/babtools_EXAMPLE',
      #packages = find_packages('.'), 
      #py_modules=['babtools_gentoo'],
      scripts=["babscript.py"]
     )
