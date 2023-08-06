#!/usr/bin/env python
# encoding: utf-8

"""pyMarkdown Minisite - Parse a list of markdown files to a website with index. 
 
Usage: 
 - parse_and_list_markdown_files.py [options] "YOUR WEBSITES NAME" PATH_TO_YOUR_FILES_DIR http://YOUR_WEBSITES.URL
  
   for default usage, or 
   
 - parse_and_list_markdown_files.py --help
   
   for getting help

Options: 
    --help - get help

    --force-update - reparse all sites and update all date tags. 
  

Examples: 
  - parse_and_list_markdown_files.py "pyMarkdown Minisite" . http://draketo.de/proj/pymarkdown_minisite/index.html
    
    Parse the site of this script. 


Plans: 
  - If an index.mdwn is present use that instead of parsing one ourself. 


Ideas: 
  - Too many, so I keep them out just now :) 

Website: U{http://draketo.de/proj/pymarkdown_minisite/}

Source URL (Mercurial): U{http://freehg.org/u/ArneBab/pymarkdown_minisite/}

PyPI URL: U{http://pypi.python.org/pypi/pymarkdown_minisite}
"""

__copyright__ = """ 
  pyMarkdown Minisite - website creation made easy
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

__version__ = "0.2"

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
