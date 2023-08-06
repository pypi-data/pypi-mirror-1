#!/usr/bin/env python
# encoding: utf-8

#    babtools_EXAMPLE - Example structure for babtools. 
# 
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

"""babtools_EXAMPLE - Example structure for babtools.
 

Usage: 
 - babscript.py 
  
   for default usage, or 
   
 - babscript.py --help
   
   for getting help
  

Examples: 
    babscript.py 


Source URL (Mercurial): U{http://freehg.org/u/ArneBab/babtools_EXAMPLE/}

PyPI URL: U{http://pypi.python.org/pypi/babtools_EXAMPLE}
"""

__version__ = "0.6"

def read_changelog():
    """Read and return the Changelog"""
    f = open("Changelog.txt", "r")
    log = f.read()
    f.close()
    return log

__changelog__ = "Changelog: \n\n" + read_changelog()


#### Self-Test ####

def _test(): 
    from doctest import testmod
    testmod()

if __name__  == "__main__": 
    
    from sys import argv
    _test()
