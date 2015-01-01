from django.db import models

# Create your models here.

class Email(models.Model):
    email = models.CharField(max_length=255)
    body = models.TextField()
    is_spam = models.BooleanField()
    # Can track later for reduced queries
    #body_len = models.PositiveIntegerField(default=0)

class Word(models.Model):
    word = models.CharField(max_length=255)
    emails = models.ManyToManyField(Email)
