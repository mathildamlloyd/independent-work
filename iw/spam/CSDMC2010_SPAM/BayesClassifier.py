from __future__ import division
from math import log, exp, floor
from numpy import std, var, mean, amin, amax
from itertools import izip_longest
from random import sample
from spam.utils import Counter, add_email
from spam.models import Email
from ProcessEmailDirectory import process_directory

def split_chunks(word_list, chunk_size, padding=""):
    """
    Takes in a list of words and splits it into chunks of size: chunk_size.
    Returns an iterable of chunks.
    If the length of the word list is not divisible by the chunk_size, empty strings will be used to pad the end of the word_list.
    Usage:
    >>> split_chunks(["a", "b", "c", "d"], 3)
    [["a", "b", "c"], ["d", "", ""]]
    """
    args = [iter(word_list)]*chunk_size
    return izip_longest(*args, fillvalue=padding)

class NaiveBayes(object):

    # TODO: FINISH FILLING IN ADDITIONAL RUN SETTINGS
    def change_settings(self, prob_method, poison_perc_train, poison_perc_test, words_per_email):

        # Note that we don't actually need to reset our training counter

        # dictionary of inserted training/testing poison words and their counts (over docs/bag-of-words)
        self.train_poison_counts  = {}
        self.testing_set = process_directory()
        self.test_poison_counts = {}
        # prob_method: probabilities drawn from doc frequencies (True) or bag-of-words frequencies (False)
        self.prob_method = prob_method
        # percentage of the training/testing spam set to poison, and amount to poison per email
        dict_file = open("/usr/share/dict/words")
        random_words = dict_file.read().splitlines()
        dict_file.close()
        email_spam_subset = list(Email.objects.filter(is_spam=True))
        no_poisoned_email = int(floor(poison_perc_train * len(email_spam_subset)))
        if self.prob_method:
            email_poison_subset = sample(email_spam_subset, no_poisoned_email)
            for poisoned_email in email_poison_subset:
                poisoned_email_wordset = poisoned_email.word_set.values_list("word", flat=True)
                for _ in xrange(words_per_email):
                    random_word = unicode(sample(random_words, 1)[0], "utf-8")
                    if random_word not in poisoned_email_wordset:
                        if random_word not in self.train_poison_counts:
                            self.train_poison_counts[random_word] = set()
                        self.train_poison_counts[random_word].add(poisoned_email.email)
            for word in self.train_poison_counts:
                self.train_poison_counts[word] = len(self.train_poison_counts[word])
        else:
            for _ in xrange(no_poisoned_email * words_per_email):
                random_word = unicode(sample(random_words, 1)[0], "utf-8")
                if random_word not in self.train_poison_counts:
                    self.train_poison_counts[random_word] = 0
                self.train_poison_counts[random_word] += 1
        # poison the testing set
        email_spam_test = sample(self.testing_set.keys(), int(floor(poison_perc_test * len(self.testing_set))))
        for email in email_spam_test:
            self.test_poison_counts[email] = []
            for _ in xrange(words_per_email):
                random_word = unicode(sample(random_words, 1)[0], "utf-8") 
                self.testing_set[email][1].append(random_word)

    def change_demo_settings(self, prob_method, poison_perc_train, poison_perc_test, words_per_email, fdir):
        # Can clean this up later since not everything is necessary

        # Note that we don't actually need to reset our training counter

        # dictionary of inserted training/testing poison words and their counts (over docs/bag-of-words)
        self.train_poison_counts  = {}
        self.testing_set = "spam/CSDMC2010_SPAM/demo/" + fdir
        self.test_poison_counts = {}
        # prob_method: probabilities drawn from doc frequencies (True) or bag-of-words frequencies (False)
        self.prob_method = prob_method
        # percentage of the training/testing spam set to poison, and amount to poison per email
        dict_file = open("/usr/share/dict/words")
        random_words = dict_file.read().splitlines()
        dict_file.close()
        email_spam_subset = list(Email.objects.filter(is_spam=True))
        no_poisoned_email = int(floor(poison_perc_train * len(email_spam_subset)))
        if self.prob_method:
            email_poison_subset = sample(email_spam_subset, no_poisoned_email)
            for poisoned_email in email_poison_subset:
                poisoned_email_wordset = poisoned_email.word_set.values_list("word", flat=True)
                for _ in xrange(words_per_email):
                    random_word = unicode(sample(random_words, 1)[0], "utf-8")
                    if random_word not in poisoned_email_wordset:
                        if random_word not in self.train_poison_counts:
                            self.train_poison_counts[random_word] = set()
                        self.train_poison_counts[random_word].add(poisoned_email.email)
            for word in self.train_poison_counts:
                self.train_poison_counts[word] = len(self.train_poison_counts[word])
        else:
            for _ in xrange(no_poisoned_email * words_per_email):
                random_word = unicode(sample(random_words, 1)[0], "utf-8")
                if random_word not in self.train_poison_counts:
                    self.train_poison_counts[random_word] = 0
                self.train_poison_counts[random_word] += 1
        # poison the testing set
        email_spam_test = sample(self.testing_set.keys(), int(floor(poison_perc_test * len(self.testing_set))))
        for email in email_spam_test:
            self.test_poison_counts[email] = []
            for _ in xrange(words_per_email):
                random_word = unicode(sample(random_words, 1)[0], "utf-8") 
                self.testing_set[email][1].append(random_word)


    # initialize classifier settings like poison amount to insert
    def __init__(self, chunk_size=7):
        self.training = Counter()
        self.CHUNK_SIZE = chunk_size
        super(NaiveBayes, self).__init__()

    def change_chunk_size(self, chunk_size):
        self.CHUNK_SIZE = chunk_size
	

    # return conditional probability of spam given input word
    def word_log_cond_prob(self, word):
        # TODO: ALSO DO THIS FOR DIFFERENT TYPES OF SMOOTHING LATER
        # TODO: COULD ALSO LATER USE ONLY EXTREME-HAM OR SPAM WORDS
        if (self.prob_method):
            p_ham = self.training.get_ham_doc_count(word)
            p_spam = self.training.get_spam_doc_count(word)
            total_ham = self.training.get_total_ham_doc_count()
            total_spam = self.training.get_total_spam_doc_count()
        else:
            p_ham = self.training.get_ham_word_count(word)
            p_spam = self.training.get_spam_word_count(word)
            total_ham = self.training.get_total_ham_word_count()
            total_spam = self.training.get_total_spam_word_count()
            for word in self.train_poison_counts:
                total_spam += self.train_poison_counts[word]
        # add in additional counts from poisoning
        if word in self.train_poison_counts:
            p_spam += self.train_poison_counts[word]
        # if word not found in both spam and ham documents, then don't count it
        if p_ham == 0 or p_spam == 0:
            return None
        # otherwise do the probability calculation, ignoring smoothing for now
        p_ham /= total_ham
        p_spam /= total_spam
        return p_spam / (p_ham + p_spam)

    # given testing email filename, return whether or not is classified spam
    # XXX: Should be deprecated to take in a list of probabilities    
    def classify_is_spam(self, email):
        raw_text = self.testing_set[email][1]
        # append any poison words to end of the email
        if email in self.test_poison_counts:
            raw_text += self.test_poison_counts[email]
        n = 0
        # calculate log probability, not counting rare or novel words
        for word in raw_text:
            p = self.word_log_cond_prob(word)
            if not p:
                continue
            n += log(1 - p) - log(p)
        return n < 0

    def get_chunk_spamicity(self, chunk):
        """
        Returns the log probability that an email is spam given a chunk of words.
        """
        n = 0
        for word in chunk:
            p = self.word_log_cond_prob(word)
            if not p:
                continue
            n += log(1 - p) - log(p)
        return n

    def chunks_to_spamicity(self, chunks):
        return [self.get_chunk_spamicity(chunk) for chunk in chunks]

    def get_email_chunk_spamicities(self, email, chunk_size):
        # Need to get raw_text
        # TODO: Is this how I do it?
        raw_text = self.testing_set[email][1]
        # append any poison words to end of the email
        if email in self.test_poison_counts:
            raw_text += self.test_poison_counts[email]
        # Split text into chunks of CHUNK_SIZE
        chunks = split_chunks(raw_text, chunk_size)
        chunk_spamicities = self.chunks_to_spamicity(chunks)
        return chunk_spamicities

    def test_heuristic(self):
	ham_stats = []
	spam_poison_stats = []
	spam_nopois_stats = []
	for email in self.testing_set:
	    stat = std(self.get_email_chunk_spamicities(email, self.CHUNK_SIZE))
	    if self.testing_set[email][0]:
		if email in self.test_poison_counts:
		    spam_poison_stats += stat
		else:
		    spam_nopois_stas += stat
	    else:
		    ham_stats += stat
	print("ham heuristic value (average, std): %d, $d" % (mean(ham_stats), std(ham_stats)))	
	print("poisoned spam heuristic value (average, std): %d, $d" % (mean(spam_poison_stats), std(spam_poison_stats))) 
	print("nopoison spam heuristic value (average, std): %d, $d" % (mean(spam_nopois_stats), std(spam_nopois_stats)))
   
    def classify_by_chunks(self, email, chunk_size=None):
	if not chunk_size:
            chunk_size = self.CHUNK_SIZE
	chunk_spamicities = self.get_email_chunk_spamicities(email, chunk_size)
        # TODO: Now that each chunk has  a spamicity value, need to do something with it...

    # calculate accuracy of the classifier over all testing emails
    def classifier_accuracy(self, retrain):
        # false positives over ham emails
        fp = 0
        # true negatives over ham emails
        tn = 0
        # false negatives over poison/non-poisoned spam emails
        fn_poisoned = 0
        fn_nonpoisoned = 0
        # true positives over poison/non-poisoned spam emails
        tp_poisoned = 0
        tp_nonpoisoned = 0
        count = 0
        for email in self.testing_set:
            count += 1
            #print("Classifying %d of %d files" % (count, len(self.testing_set)))
            actual = self.testing_set[email][0]
            predic = self.classify_is_spam(email)
            if actual == True:
                if predic == True:
                    if email in self.test_poison_counts:
                        tp_poisoned += 1
                    else:
                        tp_nonpoisoned += 1
                else:
                    if email in self.test_poison_counts:
                        fn_poisoned += 1
                    else:
                        fn_nonpoisoned += 1
            else:
                if predic == True:
                    fp += 1
                else:
                    tn += 1
        fpr = fp/(fp + tn)
        try:
            fnr_poisoned = fn_poisoned / (fn_poisoned + tp_poisoned)
        except Exception:
            fnr_poisoned = None
        try:
            fnr_nonpoisoned = fn_nonpoisoned / (fn_nonpoisoned + tp_nonpoisoned)
        except Exception:
            fnr_nonpoisoned = None
        fn = fn_poisoned + fn_nonpoisoned
        tp = tp_poisoned + tp_nonpoisoned
        fnr = fn / (fn + tp)
        acc = (tp + tn)/(fp + fn + tp + tn)
	if retrain:
	    for email in self.testing_set:
		raw_text = self.testing_set[email][1]
       		if email in self.test_poison_counts:
            	    raw_text += self.test_poison_counts[email]
		add_email(email, self.testing_set[email][0], raw_text)
        return (acc, fpr, fnr, fnr_poisoned, fnr_nonpoisoned)

    def generate_example(self):	
	email = "TRAIN_00000.eml"
        raw_text = self.testing_set[email][1]
        # append any poison words to end of the email
        if email in self.test_poison_counts:
            raw_text += self.test_poison_counts[email]
        n = 0
	f = open("example_random.txt",'a')
        # calculate log probability, not counting rare or novel words
        for word in raw_text:
            p = self.word_log_cond_prob(word)
	    f.write(word + ": " + str(p) + '\n')
            if not p:
                continue
            n += log(1 - p) - log(p)
	#for _ in xrange(15):
        #    p = self.word_log_cond_prob("looked")
	#    f.write("looked" + ": " + str(p) + '\n')
        #    if not p:
        #        continue
        #    n += log(1 - p) - log(p)
	f.write("Cumulative email spam probability, given wordset is: " + str(1/(1+exp(n))))
	f.close()
		
