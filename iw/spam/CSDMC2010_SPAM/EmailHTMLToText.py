import os
import sys
import string
from bs4 import BeautifulSoup
from spam.utils import add_word

def filter_func(char):
    return char == '\n' or 32 <= ord(char) <= 126


def parse_emails():
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
        print("Parsing %s", filename)
        f = os.path.join(srcdir, filename)
        text = ""
        with open(f) as openfileobject:
            for idx, line in enumerate(openfileobject):
                # Skip the header
                if idx <= 3:
                    pass
                text += line
        text = filter(lambda x: x in string.printable, text)
        parsed_text = BeautifulSoup(text).get_text()
        parsed_text = filter(filter_func, parsed_text).lower()
        parsed_text = parsed_text.replace("\n", " ")
        parsed_text = parsed_text.split(" ")
        for index, word in enumerate(parsed_text):
            add_word(word, True, f, index)
