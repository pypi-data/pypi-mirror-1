#!/usr/bin/env pyton
# encoding: utf-8

"""This module serves only for providing the get_all_files_in(dir) function, 
since I need it quite often.

usage: 
    >>> from get_all_files import get_all_files_in
    >>> files = get_all_files_in(".")
"""

def get_all_files_in(dir): 
	"""Return a list of all files in the given folder.

	@param dir: The path to a directory. 
	@return: A list of all files.
	"""
	from os import walk
	from os.path import join
	#: The walker shows all files and dirs in all folders (generator)
	walker = walk(dir)
	#: The list of files to be
	files = []
	for dir, dirs, filenames in walker: 
		files.extend([join(dir, filename) for filename in filenames])
	return files
