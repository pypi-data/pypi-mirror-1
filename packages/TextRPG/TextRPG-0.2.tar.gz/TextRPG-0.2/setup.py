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

"""TextRPG - A simple TextRPG which uses the 1d6 RPG backend module for character management and interaction.  

Information: http://rpg-1d6.sf.net """

from setuptools import setup, find_packages
from textrpg import __doc__ as babtools__doc__
from textrpg import __version__


def read_changelog():
    """Read and return the Changelog"""
    f = open("Changelog.txt", "r")
    log = f.read()
    f.close()
    return log

# Create the desription from the docstrings 

DESCRIPTION = __doc__.split("\n")[0].split(" - ")[1:]

LONG_DESCRIPTION = "\n".join(__doc__.split("\n")[1:])

LONG_DESCRIPTION += "\n\n" + "\n".join(babtools__doc__.split("\n")[1:])

try: 
    __changelog__ = read_changelog()
    LONG_DESCRIPTION += "\n\n" + "Changes:" + "\n\n" +  __changelog__
except: 
    pass

setup(name=__doc__.split("\n")[0].split(" - ")[0],
      version=__version__,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION, 
      author='Arne Babenhauserheide',
      author_email='arne_bab@web.de',
      keywords=["ews", "rpg", "characters", "1d6"], 
      license="GNU GPL-3 or later", 
      platforms=["any"], 
      requires = ["pyglet", "yaml"], 
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
      url='http://1w6.org/programme',
      packages = find_packages('.'), 
      #py_modules=['babtools_gentoo'],
      scripts=["ministory.py", "textrpg.py"]
     )
