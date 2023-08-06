#!/usr/bin/env python
# encoding: utf-8

#    babtools_gnutella - Tools for Gnutella clients. 
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

"""babtools_gnutella - Example structure for babtools.
 

Usage: 
 - babscript.py 
  
   for default usage, or 
   
 - babscript.py --help
   
   for getting help
  

Examples: 
  - babscript.py
    
    Print the help message, since we have nothing else to do right now. 


Plans: 
  - None. At the moment I'm happy with this structure.


Ideas: 
  - Adding information, how to use Mercurial to use this structure in your own project and keep it up to date while keeping your changes. 


Source URL (Mercurial): U{http://freehg.org/u/ArneBab/babtools_gnutella/}

PyPI URL: U{http://pypi.python.org/pypi/babtools_gnutella}
"""

__version__ = "0.1"

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


#### Functions ####

def keywords_from_files(filenames): 
    """Get a list of keywords from a list of filenames.
    
    @param files: A list of names of files.
    @type files: A list of Strings
    @returns: A set() of keywords. 
    
    Doctests: 
        >>> from os import listdir
        >>> filenames = listdir(".")
        >>> keywords_from_files(filenames)
        set(['', 'gpl', 'e4p', 'babscript', 'setup', 'py', 'babtools', 'hgtags', 'EXAMPLE', 'Changelog', 'txt', 'hg'])
    """
    #: A list of keywords. 
    keywords = filenames
    
    # Now split each file into keywords. 
    #: Characters by which the filenames get splitt - short version for bloodspell
    split_chars = ["_", ".", " ", "-", ",", "!", '"', "'", "?"]
    #: A helper list for splitting keywords
    tmp_keywords = []
    
    for i in split_chars: 
    # Create the a list of keyword lists. 
        tmp_keywords = [word.split(i) for word in keywords]
        # Empty the keywords
        keywords = []
        # And fill them with the new smaller keywords. 
        for wordlist in tmp_keywords: 
            keywords += wordlist
    
    return set(keywords)


#### Self-Test ####

def _test(): 
    from doctest import testmod
    testmod()

if __name__  == "__main__": 
    
    from sys import argv
    _test()
