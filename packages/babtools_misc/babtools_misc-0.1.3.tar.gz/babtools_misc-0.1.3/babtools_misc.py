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

Plans: 
   - None. At the moment I'm happy with this structure.


Ideas: 
   - Adding information, how to use Mercurial to use this structure 
     in your own project and keep it up to date while keeping your changes. 
   - Get the version information from the Changelog. -> i.e.: First line.split()[-1] 
     => One less point where I have to change things when updating. 


Source URL (Mercurial): U{http://bitbucker.org/ArneBab/babtools-misc/}

PyPI URL: U{http://pypi.python.org/pypi/babtools_misc}
"""

# include the docstrings from all scripts after this one. . 
import babplay_mpd_playlist, babplay_randomly, babsearch_n_replace, get_all_files
for i in [babplay_mpd_playlist, babplay_randomly, babsearch_n_replace, get_all_files]: 
    __doc__ += "\n\n## " + i.__name__ + "\n\n" + i.__doc__

__version__ = "0.1.3"

def read_changelog():
    """Read and return the Changelog"""
    try: 
        f = open("Changelog.txt", "r")
        log = f.read()
        f.close()
    except: 
        log = ""
    return log

__changelog__ = "Changelog: \n\n" + read_changelog()


#### Self-Test ####

def _test(): 
    from doctest import testmod
    testmod()

if __name__  == "__main__": 
    
    from sys import argv
    _test()
