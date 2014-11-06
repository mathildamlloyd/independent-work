import os
import sys
import string
from bs4 import BeautifulSoup

def filter_func(char):
	return char == '\n' or 32 <= ord(char) <= 126

print 'Input source directory: ' #ask for source and dest dirs
srcdir = raw_input()
if not os.path.exists(srcdir):
        print 'The source directory %s does not exist, exit...' % (srcdir)
        sys.exit()
# dstdir is the directory where the content .eml are stored
print 'Input destination directory: ' #ask for source and dest dirs
dstdir = raw_input()
if not os.path.exists(dstdir):
        print 'The destination directory is newly created.'
        os.makedirs(dstdir)

for filename in os.listdir(srcdir):
	f = os.path.join(srcdir, filename)
	text = ""
	with open(f) as openfileobject:
		for line in openfileobject:
			text += line
	text = filter(lambda x: x in string.printable, text)
	parsed_text = BeautifulSoup(text).get_text()
	parsed_text = filter(filter_func, parsed_text).lower()
	parsed_text = parsed_text.replace("\n", " ")
	parsed_text = parsed_text.split(" ")
	dstfile = open(os.path.join(dstdir, filename), 'w')
        dstfile.write(parsed_text)
        dstfile.close()

