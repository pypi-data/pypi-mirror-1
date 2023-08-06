#!/usr/bin/env python
# encoding: utf-8

"""Search and replace text strings inside text files. 

usage: 
	- babsearch_n_replace.py [options] "Search String" "Replace String" file1 dir1 file2 file3 
	  replace the text string in every text file
...

options: 
	--verbose 
	  print the files in which we found the search string. 
	--dry-run 
	  don't change any files. 
	--suffixes a list of suffixes seperated by commas. 
	  Examples: 
              "--suffixes=.txt,.html" - only .txt and .html 
              "--sufixes=" - match all files.
          Default: .txt,.mdwn,.yml,.xml,.htm,.html,.py

Decisions: 
	- No undoing, because undoing could do more harm than just replacing back 
          (would remove all new file changes -> damn unexpected!). 

Ideas: 
	- Treat linebreaks as whitespace.

"""

__copyright__ = """ 
  babsearch_n_replace - multi textfile text replace tool.
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

### Config ###

#: The list of suffixes for files in which we want to replace
suffixes = [".txt", ".mdwn", ".yml", ".xml", ".htm", ".html", ".py"]

DRY_RUN = False

VERBOSE = False

### Script ###

## General ##

def help(reason=""): 
	"""Print the help text, with an optional reason for printing it prepended"""
	print reason, __doc__


# Before we do anything else, we need the commandline arguments
from sys import argv

# We parse all command line arguments
# Actions
if "--help" in argv or "-h" in argv: 
	help()
if "--dry-run" in argv: 
	DRY_RUN = True
	argv.remove("--dry-run")
if "--verbose" in argv: 
	VERBOSE = True
	argv.remove("--verbose")
if "--suffixes=" in [i[:11] for i in argv]: 
	suff = argv[[i[:11] for i in argv].index("--suffixes=")]
	suffixes = suff[11:].split(",")
	argv.remove(suff)
if "--suffixes" in argv: 
	print suffixes 
	exit()

# And check if enough remain
if not argv[3:] and __name__ == "__main__": 
	help("""Abort: We need at least three command line arguments.

""")
	exit()

# Now import directory walking to get all files
from os import walk

# and the login name of the user
from os import getlogin
user = getlogin()

# Also we need to be able to recognize files and join paths
from os.path import isdir, isfile, join


## Replace ##

# And the replace string function
from string import replace

# We begin with building a list of paths we want want to replace
target_files = []

def replacer(targets, search_text, replace_text, dry_run=DRY_RUN): 
	"""Replaces text in the list of targets and stores backup copies of the original data in the backup_dir."""
	for target in targets: 
		# get the data
		try: 
			f = open(target, "r")
			data = f.read()
			f.close()
		except: 
			print "Couldn't read file", target
			continue
		# if the text is in there, store a backup and save the modified file.
		if search_text in data: 
			# change the data
			data = replace(data, search_text, replace_text)
			# In verbose mode print the file names
			if VERBOSE: 
				print target
			# if we do a dry run, don't change the actual target files. 
			if dry_run: 
				continue
			# write the data
			try: 
				f = open(target, "w")
				f.write(data)
				f.close()
			except: 
				print "Couldn't write to file", target
				continue


if __name__ == "__main__": 

    # Now we parse each command line argument after the first three 
    # (script name, search text, replace text). 
    # If it points to a file, we add the file directly (if it's not yet in the target_files). 
    # If it points to a directory, we walk it and add all files. 
    for path in argv[3:]: 
	    if not path in target_files: 
		    if isfile(path): 
			    target_files.append(path)
		    else: 
			    #: All files in the path
			    target_lists = [[join(dir, f) for f in files] for dir, dirs, files in walk(path)]
			    # now add all targets which aren't alread included. 
			    for targets in target_lists: 
				    target_files.extend([f for f in targets if not f in target_files])

    # Now we remove all files which don't have our text file suffixes. 
    targets = []
    for suffix in suffixes: 
	    targets.extend([f for f in target_files if f.endswith(suffix) and not f in targets])
    target_files = targets

    # Now we have a full list of files in which we want to replace the data. 
    # So we need a little file opener, replacer and saver. 
    # First the search and the replace text. 
    search_text = argv[1]
    replace_text = argv[2]


    replacer(target_files, search_text, replace_text, dry_run=DRY_RUN)
