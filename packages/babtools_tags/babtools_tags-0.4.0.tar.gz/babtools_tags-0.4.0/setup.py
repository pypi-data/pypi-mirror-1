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

"""babls - an improved "ls" which shows id3 tags for mp3 and ogg vorbis files.
"""

from setuptools import setup
from babtools_tags import __doc__ as babtools__doc__

# Create the desription from the docstrings 

DESCRIPTION = __doc__.split("\n")[0]

LONG_DESCRIPTION = "\n".join(__doc__.split("\n")[1:])

LONG_DESCRIPTION += "\n\n" + babtools__doc__

setup(name='babtools_tags',
      version='0.4.0',
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
      url='http://freehg.org/u/ArneBab/babtools_gentoo',
      #packages = find_packages('.'), 
      #py_modules=['babtools_gentoo'],
      scripts=["babls.py"]
     )
