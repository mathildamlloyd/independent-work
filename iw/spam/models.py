from django.db import models

# Create your models here.

class Word(models.Model):
    word = models.CharField(max_length=255)
    is_spam = models.BooleanField()
    email_file = models.CharField(max_length=255)
