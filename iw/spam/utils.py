from spam.models import Word
from spam.models import Email
from django.db.models import Sum

def add_word(word, email):
    w = Word.objects.get_or_create(word=word)
    w.emails.add(email)
    w.save()

def add_email(filename, is_spam, raw_text):
    e = Email.objects.get_or_create(email=filename, is_spam=is_spam, body=" ".join(raw_text))
    for word in enumerate(raw_text):
        add_word(word, e)
    e.save()
