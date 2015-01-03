from itertools import izip_longest

from spam.models import Word
from spam.models import Email
from django.db.models import Sum

def add_word(word, email):
    w = Word.objects.get_or_create(word=word)[0]
    w.emails.add(email)
    w.save()

def add_email(filename, is_spam, raw_text):
    e = Email.objects.get_or_create(email=filename, is_spam=is_spam, body=" ".join(raw_text))[0]
    for word in raw_text:
        add_word(word, e)
    e.save()


class Counter(object):
    """
    Usage:
    Tracks the counts of times a word appears within spam and ham emails.
    (Both the number of emails and the number of times).
    Should be used across multiple emails in order to decrease db queries.

    >>> c = Counter()
    >>> c.get_spam_doc_count("cow")
    """
    
    def __init__(self):
        # maps the string word to the spam_doc_count
        self.spam_doc_counter = {}
        # maps the string word to the ham_doc_count
        self.ham_doc_counter = {}
        # maps the string word to the spam_word_count
        self.spam_word_counter = {}
        # maps the string word to the ham_word_count
        self.ham_word_counter = {}
        # maps the string word to the Word class object
        self.words = {}
        # maps the string word to the queryset of Email objects
        self.emails = {}

    def get_word(self, word):
        """
        Takes in a word as a string and returns the Word object
        stored in the database or None if the word does not exist.
        """
        if word in self.words:
            return self.words[word]
        # Query for word
        q = Word.objects.filter(word=word)
        # If the word does not exist, cache so we never make the same query again
        if q.count() != 1:
            self.spam_doc_counter[word] = 0
            self.ham_doc_counter[word] = 0
            self.spam_word_counter[word] = 0
            self.ham_word_counter[word] = 0
            # Even if the word does not exist, you should store it to prevent requerying
            self.words[word] = None
            return None
        
        # Save the word
        self.words[word] = q[0]
        return q[0]

    def get_emails(self, word):
        """
        Takes in a word as a string and returns a QuerySet<Email>
        or None if the word does not exist in the database.
        """
        if word in self.emails:
            return self.emails[word]
        q = self.get_word(word)
        if not q:
            self.emails[word] = None
            return None
        emails = q.emails
        self.emails[word] = emails
        return emails
        

    def get_spam_doc_count(self, word):
        """
        Takes in a word as a string and returns the count
        of the number of spam emails that it appears in.
        """
        if word in self.spam_doc_counter:
            return self.spam_doc_counter[word]
        # Get the number of spam emails
        emails = self.get_emails(word)
        if not emails:
            self.spam_doc_counter[word] = 0
            return 0
        self.spam_doc_counter[word] = emails.filter(is_spam=True).count()
        # At this point, we can store the ham count to decrease number of operations
        self.ham_doc_counter[word] = emails.count() - self.spam_doc_counter[word]
        return self.spam_doc_counter[word]

    def get_ham_doc_count(self, word):
        """
        Takes in a word as a string and returns the count
        of the number of ham emails that it appears in.
        """
        if word in self.ham_doc_counter:
            return self.ham_doc_counter[word]
        # Get the number of ham emails
        emails = self.get_emails(word)
        if not emails:
            self.ham_doc_counter[word] = 0
            return 0
        self.ham_doc_counter[word] = emails.filter(is_spam=False).count()
        # At this point, we can store the spam count to decrease number of operations
        self.spam_doc_counter[word] = emails.count() - self.ham_doc_counter[word]
        return self.ham_doc_counter[word]

    def get_spam_word_count(self, word):
        """
        Takes in a word as a string and returns the count of the number
        of TIMES that it appears in spam emails.
        """
        if word in self.spam_word_counter:
            return self.spam_word_counter[word]
        # Get spam emails
        emails = self.get_emails(word)
        if not emails:
            self.spam_word_counter[word] = 0
            return 0
        spam_emails = list(emails.filter(is_spam=True))
        total_count = 0
        for email in spam_emails:
            total_count += email.body.count(word)
        self.spam_word_counter[word] = total_count
        return self.spam_word_counter[word]

    def get_ham_word_count(self, word):
        """
        Takes in a word as a string and returns the count of the number
        of TIMES that it appears in ham emails.
        """
        if word in self.ham_word_counter:
            return self.ham_word_counter[word]
        # Get ham emails
        emails = self.get_emails(word)
        if not emails:
            self.ham_word_counter[word] = 0
            return 0
        ham_emails = list(emails.filter(is_spam=False))
        total_count = 0
        for email in ham_emails:
            total_count += email.body.count(word)
        self.ham_word_counter[word] = total_count
        return self.ham_word_counter[word]

    def get_total_spam_word_count(self):
        if not hasattr(self, "_spam_word_count"):
            # Query for total number of words in all spam_emails
            # TODO: Add body_len field to Email model
            # self._spam_word_count = Email.objects.filter(is_spam=True).aggregate(Sum("body_len"))
            emails = list(Email.objects.filter(is_spam=True))
            # Might as well save the spam email count
            self._spam_doc_count = len(emails)
            total_len = 0
            for email in emails:
                total_len += len(email.body.split(" "))
            self._spam_word_count = total_len
        return self._spam_word_count

    def get_total_ham_word_count(self):
        if not hasattr(self, "_ham_word_count"):
            # Query for total number of words in all ham_emails
            # TODO: Add body_len field to Email model
            # self._ham_word_count = Email.objects.filter(is_spam=False).aggregate(Sum("body_len"))
            emails = list(Email.objects.filter(is_spam=False))
            total_len = 0
            for email in emails:
                total_len += len(email.body.split(" "))
            self._ham_word_count = total_len
        return self._ham_word_count

    def get_total_spam_doc_count(self):
        """
        Note: If you're going to use both get_total_spam_word_count and get_total_spam_doc_count in the same method,
        it would be better to call get_total_spam_word_count because that will calculate the doc_count as well.
        """
        if not hasattr(self, "_spam_doc_count"):
            self._spam_doc_count = Email.objects.filter(is_spam=True).count()
        return self._spam_doc_count

    def get_total_ham_doc_count(self):
        """
        Note: See get_total_spam_doc_count
        """
        if not hasattr(self, "_ham_doc_count"):
            self._ham_doc_count = Email.objects.filter(is_spam=False).count()
        return self._ham_doc_count

