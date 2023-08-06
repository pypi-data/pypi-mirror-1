#!/bin/sh

# Build the Sskreszta Log site. 
# License of this script: GPL

# This need the cmdline arguments name and path and main page. 
# $1 is the name, $2 is the path to the dynamic files, $3 the main page. 

# Please see the readme for usage instructions. 

# First enter the dir
cd $2
# Then create a static dir in there, if there isn't already one. 
mkdir -p static
# Copy the style template in there
cp templates/style.css static/

# First create the markdown content of the index page. 

# The header
echo "$1" > static/index.mdwn
echo "======================" >> static/index.mdwn
# And the list of files. 
for i in *mdwn
  do echo "* [$i]($i.html)" >> static/index.mdwn
  # Add an empty line. 
  echo "" >> static/index.mdwn
done
# At the end, add a link back to the main site. 
echo "[$3]($3)" >> static/index.mdwn

# Then compile it to html. 

# use the header template file for the index
cat templates/index_head.html | sed s/"MARKDOWN_LIST"/"$1"/ > static/index.html
# Compile it to markdown
markdown.py -e utf-8 static/index.mdwn >> static/index.html
# and add the footer template
cat templates/index_foot.html >> static/index.html

rm static/index.mdwn

# And compiile every entry to html. 

for i in *.mdwn
  # First each files header template
  do cat templates/file_head.html | sed s/"MARKDOWN_LIST"/"$i"/ > static/$i.html
  # Then the content
  markdown.py $i >> static/$i.html
  # a backlink 
  echo "<a href='index.html'>$1</a>" >> static/$i.html
  # And in the end the footer. 
  cat templates/file_foot.html >> static/$i.html
done

