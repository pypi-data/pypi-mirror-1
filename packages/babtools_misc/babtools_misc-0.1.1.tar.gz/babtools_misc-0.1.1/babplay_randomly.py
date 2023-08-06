#!/usr/bin/env python
# encoding: utf-8

"""Tell mplayer to randomly play all passed files. 

usage: babplay_randomly.py [--help] [-fs] [-caca] [DIR DIR ...] [FILE FILE ...]
"""

__copyright__ = """ 
  babplay_randomly - Play all files in a folder at random (using mplayer)
----------------------------------------------------------------- 
© 2008 - 2009 Copyright by Arne Babenhauserheide

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
  MA 02110-1301 USA

""" 

# First we need to be able to get the list of files
from sys import argv

def help(): 
	"""Generate a help text."""
	return __doc__ 

if "--help" in argv: 
	print help()
	exit()

# Be able to recognize directories. 
from os.path import isdir, join
from os import listdir
# And walk a directory tree. 
from os import walk

# And we want to be able to shuffle the list. 
from random import shuffle

# Then we need to be able to start mpplayer. We want it to wait until mplayer finished, so we get teh function call. 
from subprocess import call

#: The line to call mplayer: 
MPLAYER = ["mplayer", "-framedrop", "-zoom"]

# Take over the "-fs" option from the command line to mplayer (full screen)
if "-fs" in argv: 
	MPLAYER.append("-fs")
	argv.remove("-fs")

if "-caca" in argv: 
	MPLAYER.append("-vo")
	MPLAYER.append("caca")
	argv.remove("-caca")

# First get the list of files. 
files = argv[1:]

# If the list is empty, add the current dir
if not files: 
	files.append(".")

# Check for directories - replace them with their contents. 
def replace_dirs_with_their_contents(files): 
	"""Replace each directory with the files it contains."""
	new_files = []
	for i in files: 
		# directly add files
		if not isdir(i): 
			new_files.append(i)
		# but check the contents of dirs. 
		else: 
			try: 
				for dir_path, dirs, dir_files in [i for i in walk(i)]: 
					new_files += [join(dir_path, f) for f in dir_files]
			except: 
				pass
	return new_files

files = replace_dirs_with_their_contents(files)


# Now shuffle it
shuffle(files)

if __name__ == "__main__": 
    # now call mplayer for each batch of 100 (bash-)escaped filename. 
    for i in range(len(files)/100 +1 ):
	call(MPLAYER + [j.encode("string-escape") for j in files[i:]])

    # That should have done it. 
