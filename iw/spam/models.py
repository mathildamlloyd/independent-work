from django.db import models

# Create your models here.

class Word(models.Model):
    word = models.CharField(max_length=255)
    spam_docs = models.IntegerField()
    spam_count = models.IntegerField()
    ham_docs = models.IntegerField()
    ham_count = models.IntegerField()
