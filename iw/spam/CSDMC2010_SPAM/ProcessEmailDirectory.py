import os
import sys
from spam.utils import add_email
from EmailHTMLToText import parse_email

# populate the training database with emails from specified source directory
def train_database():
    processed_emails = process_directory()
    for email in processed_emails:
        add_email(email, processed_emails[email][0], processed_emails[email][1])

# process all of the emails from a specified source directory
def process_directory():
    print("Input source directory: ")
    srcdir = raw_input()
    while not os.path.exists(srcdir):
        print("The source directory %s does not exist" %(srcdir))
        print("Input source directory: ")
        srcdir = raw_input()
    labels = {}
    with open(os.path.join(srcdir + "/..", "SPAMTrain.label")) as openfileobject:
        for idx, line in enumerate(openfileobject):
            label = line.replace("\n", "").split(" ")
            labels[label[1]] = label[0]
    processed_emails = {}
    count = 0
    total = len(os.listdir(srcdir))
    for filename in os.listdir(srcdir):
        count += 1
        print("Processing %d of %d files" % (count, total))
        f = os.path.join(srcdir, filename)
        raw_text = parse_email(f)
        is_spam = labels[filename] == "0"
        processed_emails[filename] = (is_spam, raw_text)
    return processed_emails
