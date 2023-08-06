#!/usr/bin/env python
# encoding: utf-8

#    babls - an improved "ls" which shows id3 tags for mp3 and ogg vorbis files.
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

"""babscript - doing something bab. """

def help(): 
    """Help message"""
    from babtools_EXAMPLE import __doc__ as babtools__doc__
    return "\n\n".join(babtools__doc__.split("\n\n")[:4])


#### Run ####

def main(args):
    """Run the script."""
    print help() # :) 

#### Self-Test ####

def _test(): 
    from doctest import testmod
    testmod()

if __name__  == "__main__": 
    
    from sys import argv
    if len(argv) > 1 and argv[1] in ["--help", "-h"] : 
        print help()
    else: 
        main(argv[1:]) 
