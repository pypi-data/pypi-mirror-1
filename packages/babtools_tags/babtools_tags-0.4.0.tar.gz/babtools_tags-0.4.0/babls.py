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

"""babls - an improved "ls" which shows id3 tags for mp3 and ogg vorbis files. """

from tagpy import FileRef
from os import listdir
from os.path import isfile, isdir, join

def ls(paths=None):
    if paths is None: 
        DIRS = ["."]
    else: 
        DIRS = paths
    for j in DIRS: 
        if isdir(j): 
            print ""
            print "# All files and folders in " + j + " with some metadata."
            files = listdir(j)
            files.sort()
            for i in files: 
                if isfile(join(j, i)): 
                    print_with_metadata(join(j, i))
                else:
                    print "\n" + join(j, i)
            print ""
        elif isfile(j): 
            print_with_metadata(j)
        else: 
            print "\n" + j

def print_with_metadata(path):
    """Print metadata for a file, if avaible"""
    print path
    try: 
	f = FileRef(path)
	if hasattr(f, "file"):
	    a = f.file()
	    if hasattr(a, "ID3v2Tag"): 
		tag = a.ID3v2Tag()
		if hasattr(tag, "title"): 
		    print " - Title:", tag.title
		if hasattr(tag, "artist"): 
		    print " - Artist:", tag.artist
		if hasattr(tag, "album"): 
		    print " - Album:", tag.album
                # Add an empty line
                print ""
    except: pass


def help(): 
    """Help message"""
    from babtools_tags import __doc__ as babtools__doc__
    return "\n\n".join(babtools__doc__.split("\n\n")[:4])

def _test(): 
    from doctest import testmod
    testmod()

if __name__  == "__main__": 
    
    from sys import argv
    if len(argv) == 1: 
        # The script was called without arguments
        ls()
    elif argv[1] == "--help": 
        print help()
    else: 
        # pass all args to the script. 
        ls(paths=argv[1:])
