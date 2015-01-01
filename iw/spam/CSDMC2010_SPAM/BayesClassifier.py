from ProcessEmailDirectory import process_directory

class NaiveBayes():

    # initialize classifier settings like poison amount to insert
    def __init__(self, poison_perc_train, poison_perc_test):
        self.train_poison_counts = {}
        self.test_poison_counts = {}
        self.testing_set = process_directory()
        # FILL IN HOW TO DO POISONING LATER

    # return conditional probability of spam given input word
    def word_log_cond_prob(self, word):
        # LATER DO THIS FOR BOTH FREQUENCY AND WORD APPEARANCE
        # ALSO DO THIS FOR DIFFERENT TYPES OF SMOOTHING LATER
        # COULD ALSO LATER USE ONLY EXTREME-HAM OR SPAM WORDS
        p1 = (get_spam_doc_count(word) + 1)/(get_total_spam_docs + get_total_training_words)
        p2 = (get_ham_doc_count(word) + 1)/(get_total_ham_docs + get_total_training_words)
        return p1/(p1 + p2)

    # given testing email filename, return whether or not is classified spam
    def classify_is_spam(self, email):
        raw_text = self.testing_set[email][1].split(" ")
        n = 0
        for word in raw_text:
            p = word_log_cond_prob(word)
            n += math.log(1 - p) - math.log(p)
        return 1/(1 + math.exp(n)) > 0.5

    # calculate accuracy of the classifier over all testing emails
    def classifier_accuracy(self):
        fp = 0
        fn = 0
        tp = 0
        tn = 0
        for email in self.testing_set:
            actual = self.testing_set[email][0]
            predic = classify_is_spam(email)
            if actual == True:
                if predic == True:
                    tp += 1
                else:
                    fn += 1
            else:
                if predic == True:
                    fp += 1
                else:
                    tn += 1
        fpr = fp/(fp + tn)
        fnr = fn/(fn + tp)
        acc = (tp + tn)/(fp + fn + tp + tn)
        return (acc, fpr, fnr)
