from spam.models import Word

def add_word(word, is_spam, file_name, index):
    # See if it is already in the db
    w, created = Word.objects.get_or_create(word=word, is_spam=is_spam, email_file=file_name, index=index)
    if created:
        w.save()
