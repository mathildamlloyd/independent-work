from spam.models import Word
from django.db.models import Sum

def add_word(word, is_spam, is_novel_occurrence):
    # check if word already contained in db
    w = Word.objects.filter(word=word)
    if len(w) == 0:
        w = Word(word=word, spam_docs=0, spam_count=0, ham_docs=0, ham_count=0)
    else:
        w = w[0]
    # deal with spam and ham cases
    if is_spam:
        w.spam_count += 1
        if is_novel_occurrence:
            w.spam_docs += 1
    else:
        w.ham_count += 1
        if is_novel_occurrence:
            w.ham_docs += 1
    w.save()

def get_training_freq(word):
    # check if word is in db, otherwise return null
    w = Word.objects.filter(word=word)
    if len(w) == 0:
        return None
    else:
        w = w[0]
        return (word.ham_docs, word.spam_docs, word.ham_count, word.spam_count)

def get_totals():
    return Word.objects.aggregate(Sum('ham_count'), Sum('spam_count'))
