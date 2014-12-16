from spam.models import Word

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
