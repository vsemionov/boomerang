from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Notebook(models.Model):
    user = models.ForeignKey("auth.User")
    name = models.CharField(max_length=128)


class Note(models.Model):
    notebook = models.ForeignKey(Notebook)
    title = models.CharField(max_length=128)
    text = models.TextField()


class Task(models.Model):
    user = models.ForeignKey("auth.User", editable=False)
    done = models.BooleanField()
    title = models.CharField(max_length=128)
    description = models.TextField()
