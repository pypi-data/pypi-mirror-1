#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""pyMarkdown Minisite - Parse and list markdown files. 

A somewhat more advanced version of the simple shell script - written for pymarkdown minisite.
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

# This need the cmdline arguments name and path and main page. 
# $1 is the name, $2 is the path to the dynamic files, $3 the main page. 

# Please see the readme for usage instructions. 
# We need some file operations
from os import chdir, mkdir, listdir, curdir
from os.path import isdir, join, isfile, abspath
# And command line arguments
from sys import argv
# Also some string functions. 
from string import replace
# For timestamping some timestamps - I like it to know when sites where last changed :) 
from time import strftime
# And naturally markdown :) 
from markdown import Markdown

def help(): 
    """Give usage instructions."""
    return '''Usage: 
    parse_and_list_markdown_files.py [options] "YOUR WEBSITES NAME" . http://BACKLINK.URL

Options: 
    --encoding     specifies the encoding; example: --encoding utf-8

    --force-update forces rebuilding every page 
		   instead of only the changed ones. 
                   It is useful, since changes in the footer are 
		   invisible to the algorithm. '''

# And create some constants. 
TARGET_DIR = "static"
TEMPLATE_DIR = "templates"
STYLESHEET_NAME = "style.css" # inside the templates dir. 
FILE_ENCODING = "utf-8"
FILE_SUFFIXES = [".mdwn", ".txt"]

# Before I really begin, add some "I am lazy and that is good" functions :) 

def read_file(path): 
    """Read all data from a file. 

If the file doesn't exist, just return an empty string.
"""
    try: 
	f = open(path, "r")
	# read the data as unicode
	try: 
	    data = unicode(f.read(), FILE_ENCODING)
	except: 
	    print "Input files must be encoded in", FILE_ENCODING
	    # Leave the script now. 
	    exit()
	f.close()
    except: 
	data = u""
    return data

def write_file(path, data): 
    """Write all data into a file at the path - overwrite existing data.

Raise an (automatic) exception if it doesn't work. 
"""
    f = open(path, "w")
    f.write(data.encode(FILE_ENCODING))
    f.close()


## Begin parsing code

def prepare_the_target_dir(DIR_WITH_FILES, SITENAME, TARGET_DIR, LINK_BACK): 
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
def write_the_index(DIR_WITH_FILES, SITENAME, TARGET_DIR, LINK_BACK, force_update = False): 
    """Write the index file - if anything was changed, add a new timestamp."""
    index = ""

    ## First the header
    # The sitename = title
    index += SITENAME
    # Make it a title: 
    index += "\n================="

    ## Now the list of files
    for i in listdir(DIR_WITH_FILES): 
	# Add a list of all markdown files
	for suffix in FILE_SUFFIXES: 
	    if i.endswith(suffix): 
		# but remove the suffix and leave an empty line before each entry. 
		index += "\n\n* [" + i[:-len(suffix)] + "](" + i[:-len(suffix)] + ".html)"

    # At the end, add a link back to the main site. 
    index += "\n\n[" + LINK_BACK + "](" + LINK_BACK + ")"
    
    # Also add a date and time line. 
    index += "\n\n --- " # A seperator - looks better. 
    index += "\n\n -- *" + strftime('%Y-%m-%d %H:%M:%S') + "* --"

    ## Then compile it to html. 

    # First get the header from the template. 
    data = read_file(join(TEMPLATE_DIR, "index_head.html"))
    # Now replace the title
    data = replace(data, "MARKDOWN_LIST", SITENAME)

    # Compile the index to markdown - now is the first time we really need markdown :) 
    md = Markdown(extensions=['toc'])
    data += md.convert(index)
    # and add the footer template
    data += read_file(join(TEMPLATE_DIR, "index_foot.html"))

    # Now save the file. 
    write_file(join(TARGET_DIR, "index.html"), data)


# And compile every mdwn file to html

def write_all_content_files(DIR_WITH_FILES, SITENAME, TARGET_DIR, LINK_BACK, force_update = False): 
    """Compile all files in the dir with the .mdwn suffix to html and put them into the target dir."""
    # We need markdown again. 
    md = Markdown(extensions=['toc'])

    ## Now the list of files
    #: tracks if any file changed. 
    changed = False
    for i in listdir(DIR_WITH_FILES): 
	# Add a list of all markdown files
	for suffix in FILE_SUFFIXES: 
	    if i.endswith(suffix): 
		# First read the current data. 
		# If it starts the same way (till the Markdown part finishes) the file didn't change, 
		# and we don't touch it. 
		old_data = read_file(join(TARGET_DIR, i[:-len(suffix)] + ".html"))
		# First check the file. If nothing changed, don't change it (and don't update the timestamp). 
		data = read_file(join(TEMPLATE_DIR, "file_head.html"))
		# replace the title. 
		data = replace(data, "MARKDOWN_LIST", SITENAME)
		# Now convert the content. 
		markdown_data = read_file(i)
		data += md.convert(markdown_data)
		# if now old_data and new data fit, we jump to the next document, 
		# except if all sites MUST be reparsed. 
		if old_data[:len(data)] == data and not force_update: 
		    continue
		# If we get till here, the site changed and we need a new date line. 
		changed = True
		# and add a backlink and a date-line. 
		data += "\n<a href='index.html'>" + SITENAME + "</a>"
		data += "\n<hr>"
		data += "\n<p> -- <em>" + strftime('%Y-%m-%d %H:%M:%S') + "</em> -- </p>"
		# And in the end the footer. 
		data += read_file(join(TEMPLATE_DIR, "file_foot.html"))
		# and write the file. 
		write_file(join(TARGET_DIR, i[:-len(suffix)] + ".html"), data)
    
    # We return the changed info, so the index only needs to be rebuilt, if some file changed. 
    return changed

# That's it! 

# Now because I'm damn lazy: Write a wrap function :) 

def parse_sites(DIR_WITH_FILES, SITENAME, TARGET_DIR, LINK_BACK, force_update = False): 
    """Create the index and parse the content files."""
    # Fix bad source folders - make the path absolute. 
    if not abspath(DIR_WITH_FILES) == DIR_WITH_FILES: 
	DIR_WITH_FILES = join(abspath(curdir), DIR_WITH_FILES)

    prepare_the_target_dir(DIR_WITH_FILES = DIR_WITH_FILES, SITENAME = SITENAME, TARGET_DIR = TARGET_DIR, LINK_BACK = LINK_BACK)

    changed = write_all_content_files(DIR_WITH_FILES = DIR_WITH_FILES, SITENAME = SITENAME, TARGET_DIR = TARGET_DIR, LINK_BACK = LINK_BACK, force_update = force_update)

    # Only parse the index, if tehre isn't yet an index file."
    if not "index.mdwn" in listdir(DIR_WITH_FILES) and changed or not "index.mdwn" in listdir(DIR_WITH_FILES) and force_update: 
	write_the_index(DIR_WITH_FILES = DIR_WITH_FILES, SITENAME = SITENAME, TARGET_DIR = TARGET_DIR, LINK_BACK = LINK_BACK, force_update = force_update)


#### Self-Test ####

def _test(): 
    from doctest import testmod
    testmod()

if __name__ == "__main__": 
    # Provide help, if the commandline args don't fit. 
    if len(argv) < 4 or len(argv) == 2 and argv[1] == "--help": 
	print help()
    elif len(argv) > 1 and argv[1] == "--help": 
	print help()
    else: 

	# Parse the commandline arguments. 
	SITENAME = argv[-3]
	DIR_WITH_FILES = argv[-2]
	LINK_BACK = argv[-1]
	# Check if the user wants to force an update. 
	if "--force-update" in argv[:-3]: 
	    force_update = True
	else: 
	    force_update = False
	# Also check, if the user specifies an encoding. 
	# This should allow for fixing all unicode read errors. 
	# The encoding is used by unicode() to set the encoding. 
	if "--encoding" in argv[:-3]: 
	    FILE_ENCODING = argv[argv.index("--encoding") +1]

	parse_sites(DIR_WITH_FILES = DIR_WITH_FILES, # Where the markdown files are
			SITENAME = SITENAME, # The name of the site - Title and heading. 
			TARGET_DIR = TARGET_DIR, # The dir, where the html should be stored. 
			LINK_BACK = LINK_BACK, # The link to the users main site (or any other site)
			force_update = force_update # If all sites MUST be parsed again - can be useful for template development. 
		    )
