#!/usr/bin/env python
# encoding: utf-8

"""Use mplayer to play an mpd playlist. 

Usage: 
    babplay_mpd_playlist.py [options] <playlist without suffix>

Options: 
    --random 	shuffle list before playing

Dependencies: 
	* shell
	* cat
	* sed
	* mplayer


"""

__copyright__ = """ 
  babplay_mpd_playlist - Use mplayer to play mpd playlist(s)
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

MPD_PATH = "/var/lib/mpd"

# First we need to parse the command line arguments. 
from sys import argv
if "--help" in argv: 
	print "Usage:", argv[0], "[options] <playlist without suffix>"
	exit()

#: Commandline options
opts = {}

# Remove the first argv
argv = argv[1:]

# Check for commandline arguments. 
if "--random" in argv: 
    opts["random"] = True
    argv.remove("--random")


def get_playlist_files(playlist_filename): 
    """Get a list of absolute strings with teh files in the playlist."""
    # Get the playlist data
    from os.path import join
    playlist_dir = join(MPD_PATH, "playlists")
    f = open(join(playlist_dir, playlist_filename))
    playlist = f.read()
    f.close()

    #: The music dir of mpd (with symlinks)
    mpd_music_dir = join(MPD_PATH, "music")

    # Get the files to play by splitting the lines. 
    files_to_play = playlist.splitlines()
    # Now make them absolute (all are in the mpd_music_dir) 
    # and add "" around them. 
    files_to_play = ['"' + join(mpd_music_dir, i) + '"' for i in files_to_play]
    return files_to_play


def play(files_to_play):
    # at last, make them seperated by line number. 
    files_to_play_string = r" ".join(files_to_play)

    # Now escape "`"
    import string
    files_to_play_string = string.replace(files_to_play_string, "`", r"\`")

    # Now just call mplayer as subprocess, adding . 
    from subprocess import call

    # Call the shell 
    call('mplayer ' + files_to_play_string, shell=True)

if __name__ == "__main__": 

    # Get the file paths
    playlist_files = []
    for playlist_name in argv: 
	playlist_files += get_playlist_files(playlist_name + ".m3u")
    if "random" in opts and opts["random"]: 
	from random import shuffle
	shuffle(playlist_files)

    # Call the files to play in batches of 100 to avoid putting too many arguments 
    # into the shell. 

    if len(playlist_files) < 100: 
	play(playlist_files)
    else: 
	for i in range(len(playlist_files) / 100): 
	    play(playlist_files[i*100:(i+1)*100])
