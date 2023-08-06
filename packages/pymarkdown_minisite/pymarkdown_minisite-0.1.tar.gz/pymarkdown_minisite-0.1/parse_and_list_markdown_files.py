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

"""pyMarkdown Minisite - Parse and list markdown files. 

A somewhat more advanced version of the simple shell script - written for pymarkdown minisite.
"""

# This need the cmdline arguments name and path and main page. 
# $1 is the name, $2 is the path to the dynamic files, $3 the main page. 

# Please see the readme for usage instructions. 
# We need some file operations
from os import chdir, mkdir, listdir
from os.path import isdir, join
# And command line arguments
from sys import argv
# Also some string functions. 
from string import replace
# And naturally markdown :) 
from markdown import Markdown

def help(): 
    """Give usage instructions."""
    return 'Usage: parse_and_list_markdown_files.py "YOUR WEBSITES NAME" . http://YOUR_WEBSITES.URL'

# And create some constants. 
TARGET_DIR = "static"
TEMPLATE_DIR = "templates"
STYLESHEET_NAME = "style.css" # inside the templates dir. 

# Before I really begin, add some "I am lazy and that is good" functions :) 

def read_file(path): 
    """Read all data from a file."""
    f = open(path, "r")
    data = f.read()
    f.close()
    return data

def write_file(path, data): 
    """Write all data into a file at the path - overwrite existing data."""
    f = open(path, "w")
    f.write(data)
    f.close()


## Begin parsing code

def prepare_the_target_dir(SITENAME, TARGET_DIR, LINK_BACK): 
    # First enter the dir
    chdir(DIR_WITH_FILES)
    # Then create a static dir in there, if there isn't already one. 
    if not isdir(TARGET_DIR): 
	mkdir(TARGET_DIR)

    # Copy the style template in there

    # Read the data and write it to the target file. 
    data = read_file(join(TEMPLATE_DIR, STYLESHEET_NAME))
    write_file(join(TARGET_DIR, STYLESHEET_NAME), data)

# Now create the markdown content of the index page. 
def write_the_index(SITENAME, TARGET_DIR, LINK_BACK): 
    """WRite the index file."""
    index = ""

    ## First the header
    # The sitename = title
    index += SITENAME
    # Make it a title: 
    index += "\n================="

    ## Now the list of files
    for i in listdir("."): 
	# Add a list of all markdown files
	if i.endswith(".mdwn"): 
	    # but remove the suffix and leave an empty line before each entry. 
	    index += "\n\n* [" + i[:-5] + "](" + i[:-5] + ".html)"

    # At the end, add a link back to the main site. 
    index += "\n\n[" + LINK_BACK + "](" + LINK_BACK + ")"

    ## Then compile it to html. 

    # First get the header from the template. 
    data = read_file(join(TEMPLATE_DIR, "index_head.html"))
    # Now replace the title
    data = replace(data, "MARKDOWN_LIST", SITENAME)

    # Compile the index to markdown - now is the first time we really need markdown :) 
    md = Markdown()
    data += md.convert(index)
    # and add the footer template
    data += read_file(join(TEMPLATE_DIR, "index_foot.html"))

    # Now save the file. 
    write_file(join(TARGET_DIR, "index.html"), data)


# And compile every mdwn file to html

def write_all_content_files(SITENAME, TARGET_DIR, LINK_BACK): 
    """Compile all files in the dir with the .mdwn suffix to html and put them into the target dir."""
    # We need markdown again. 
    md = Markdown()

    ## Now the list of files
    for i in listdir("."): 
	# Add a list of all markdown files
	if i.endswith(".mdwn"): 
	    data = read_file(join(TEMPLATE_DIR, "file_head.html"))
	    # replace the title. 
	    data = replace(data, "MARKDOWN_LIST", SITENAME)
	    # Now convert the content. 
	    markdown_data = read_file(i)
	    data += md.convert(markdown_data)
	    # and add a backlink. 
	    data += "<a href='index.html'>" + SITENAME + "</a>"
	    # And in the end the footer. 
	    data += read_file(join(TEMPLATE_DIR, "file_foot.html"))
	    # and write the file. 
	    write_file(join(TARGET_DIR, i[:-5] + ".html"), data)

# That's it! 

# Now because I'm damn lazy: Write a wrap function :) 

def parse_sites(SITENAME, TARGET_DIR, LINK_BACK): 
    """Create the index and parse the content files."""
    prepare_the_target_dir(SITENAME = SITENAME, TARGET_DIR = TARGET_DIR, LINK_BACK = LINK_BACK)
    write_the_index(SITENAME = SITENAME, TARGET_DIR = TARGET_DIR, LINK_BACK = LINK_BACK)
    write_all_content_files(SITENAME = SITENAME, TARGET_DIR = TARGET_DIR, LINK_BACK = LINK_BACK)


#### Self-Test ####

def _test(): 
    from doctest import testmod
    testmod()

if __name__ == "__main__": 
    # Provide help, if the commandline args don't fit. 
    if len(argv) != 4 or len(argv) == 2 and argv[1] == "--help": 
	print help()
    elif len(argv) > 1 and argv[1] == "--help": 
	print help()
    else: 

	# Parse the commandline arguments. 
	SITENAME = argv[1]
	DIR_WITH_FILES = argv[2]
	LINK_BACK = argv[3]

	parse_sites(SITENAME = SITENAME, TARGET_DIR = TARGET_DIR, LINK_BACK = LINK_BACK)
