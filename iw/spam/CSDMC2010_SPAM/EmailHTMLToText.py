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

    # get training labels for email set
    labels = {}
    with open(os.path.join(srcdir + "/..", "SPAMTrain.label")) as openfileobject:
        for idx, line in enumerate(openfileobject):
            label = line.replace("\n", "").split(" ")
            labels[label[1]] = label[0]

    count = 0
    total = len(os.listdir(srcdir))

    for filename in os.listdir(srcdir):
        count += 1
        print("Processing %d of %d files" % (count, total))
        f = os.path.join(srcdir, filename)
        f_new = open(os.path.join(dstdir, filename), 'w')
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
        # Save cleaned text to new file for review
        f_new.write(parsed_text)
        parsed_text = parsed_text.replace("\n", " ")
        parsed_text = parsed_text.split(" ")
        # Get the training label for the current email being parsed
        is_spam = labels[filename] == "0"
        email_wordset = set()
        for index, word in enumerate(parsed_text):
            if word in email_wordset:
                add_word(word, is_spam, False)
            else:
                add_word(word, is_spam, True)
            email_wordset.add(word)
        f_new.close()
