import os
import sys
import string
from bs4 import BeautifulSoup
from spam.utils import get_training_freq
from spam.utils import get_totals

class BayesClassifier():

    def __init__(self):
        self.poisoned = {}
        totals = Word.get_totals()
        self.ham_docs_total = 2949
        self.spam_docs_total = 1378
        self.ham_count_total = totals["ham_count__sum"]
        self.spam_count_total = totals["spam_count__sum"]

    def nbayes_unpoisoned(self):
        # get spam source directory
         print 'Input source directory: '
        srcdir = raw_input()
        if not os.path.exists(srcdir):
            print "The source directory %s does not exist, exit..." % (srcdir)
            return
        # get naive bayes classification settings
        print "Naive Bayes Spam Classification preferences"
        print "-------------------------------------------"
        print "1) Spam/ham likelihood weighting settings:"
        print "a - Include likelihood bias"
        print "b - Equal spam/ham weighting"
        print "(Choose a/b) ... "
        set_eq_weighting = raw_input()
        if not (set_eq_weighting == "a" or set_eq_weighting == "b"):
            print "Invalid selection, exit..."
            return
        else:
            set_eq_weighting = (set_eq_weighting == "b")
        print "2) Joint probability combining settings:"
        print "a - Naive Bayes combining"
        print "b - Chi-square combining"
        print "(Choose a/b) ... "
        set_naive_comb = raw_input()
        if not (set_naive_comb == "a" or set_naive_comb == "b"):
            print "Invalid selection, exit..."
            return
        else:
            set_naive_comb = (set_naive_comb == "a")
        print "3) Rare word occurrence handling:"
        print "a - Weighted confidence smoothing"
        print "b - Laplace smoothing"
        print "(Choose a/b) ... "
        set_lap_smooth = raw_input()
        if not (set_lap_smooth == "a" or set_lap_smooth == "b"):
            print "Invalid selection, exit..."
            return
        else:
            set_lap_smooth = (set_lap_smooth == "b")
        # choose poisoning settings
        print "4) Poisoning preferences:"
        print "Percentage of training set to poison:"
        poison_perc_trn = None
        while not (poison_perc_trn and poison_perc_trn <= 100 and poison_perc_trn >= 0):
            poison_perc_trn = prompt_num() 
        print "Percentage of testing set to poison:"
        poison_perc_tst = None
        while not (poison_perc_tst and poison_perc_tst <= 100 and poison_perc_tst >= 0):
            poison_perc_tst = prompt_num()
        
        
        for filename in os.listdir(srcdir):
            count += 1
            print("Processing %d of %d files" % (count, total))
            f = os.path.join(srcdir, filename)

    def filter_func(char):
        return char == '\n' or 32 <= ord(char) <= 126
    
    def prompt_num():
        try:
            num = int(raw_input())
            return num
        except Exception:
            print "Not a valid number input"
            return None

    def parse_email(srcdir, filename):
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
        return parsed_text
