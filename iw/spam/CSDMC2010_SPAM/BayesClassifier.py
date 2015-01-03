from __future__ import division
from math import log, exp, floor
from random import sample
from spam.utils import Counter
from spam.models import Email
from ProcessEmailDirectory import process_directory

class NaiveBayes():

    # initialize classifier settings like poison amount to insert
    def __init__(self, prob_method, poison_perc_train, poison_perc_test, words_per_email):
        # TODO: FINISH FILLING IN ADDITIONAL RUN SETTINGS
        # dictionary of inserted training/testing poison words and their counts (over docs/bag-of-words)
        self.train_poison_counts  = {}
        self.test_poison_counts = {}
        # dictionary of test emails to their spam value and text body
        self.testing_set = process_directory()
        # cache of training database
        self.training = Counter()
        # prob_method: probabilities drawn from doc frequencies (True) or bag-of-words frequencies (False)
        self.prob_method = prob_method
        # percentage of the training/testing spam set to poison, and amount to poison per email
        random_words = open("/usr/share/dict/words").read().splitlines()
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

    # calculate accuracy of the classifier over all testing emails
    def classifier_accuracy(self):
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
            print("Classifying %d of %d files" % (count, len(self.testing_set)))
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
        return (acc, fpr, fnr, fnr_poisoned, fnr_nonpoisoned)
