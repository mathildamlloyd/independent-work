from spam.CSDMC2010_SPAM.BayesClassifier import NaiveBayes
from shutil import copyfile

BASE_DIR = "spam/CSDMC2010_SPAM/demo/"

class Demo(object):

    def run(self, doc_count=True):
        print("Would you like to try a high spamicity or low spamicity spam email?")
        print("1: high spam")
        print("2: low spam")
        # Prompt for which file to use
        fname = raw_input()
        while fname != "1" or fname != 2:
            print("Would you like to try a high spamicity or low spamicity spam email?")
            print("1: high spam")
            print("2: low spam")

        classifier = NaiveBayes()
        fdir = BASE_DIR + "src/" + fname
        n.change_demo_settings(doc_count, 0, 1, 0, fdir)
        # Classify the original file
        original = n.classifier_accuracy(False)
        print("Original email:")
        with open(fdir+"/" + fname, "r") as fin:
            print fin.read()
        self.print_accuracy(poisoned, False)
        # We want to copy the correct file to a reusable location
        copyfile(BASE_DIR + "src/" + fname, BASE_DIR + "dst/" + fname)
        # Prompt to add poison
        print("Please type in the poisoned text that you would like to append to the end of the email")
        extra_poison = raw_input()
        fdir = BASE_DIR + "dst/" + fname
        f = open(fdir + "/" + fname, "a")
        f.write(extra_poison)
        f.close()
        n.change_demo_settings(doc_count, 0, 1, 0, fdir)
        poisoned = n.classifier_accuracy(False)
        self.print_accuracy(poisoned, True)


    def print_accuracy(self, results, poisoned):
        if poisoned:
            print("Printing results for poisoned email:")
        else:
            print("Printing results for original email:")
        print("Accuracy: " + str(results[0]))
        print("False Positive Rate: " + str(results[1]))
        print("False Negative Rate: " + str(results[2]))
