from django.db import models

# Create your models here.

class Email(models.Model):
    email = models.CharField(max_length=255)
    body = models.TextField()
    is_spam = models.BooleanField()

class Word(models.Model):
    word = models.CharField(max_length=255)
    emails = models.ManyToManyField(Email)
