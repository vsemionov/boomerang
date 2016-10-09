from __future__ import unicode_literals

from django.db import models

# Create your models here.

MAX_NAME_SIZE = 128


class Notebook(models.Model):
    user = models.ForeignKey("auth.User")
    name = models.CharField(max_length=MAX_NAME_SIZE)

    def __unicode__(self):
        return self.name


class Note(models.Model):
    notebook = models.ForeignKey(Notebook)
    title = models.CharField(max_length=MAX_NAME_SIZE)
    text = models.TextField()

    def __unicode__(self):
        return self.title


class Task(models.Model):
    user = models.ForeignKey("auth.User")
    done = models.BooleanField(default=False)
    title = models.CharField(max_length=MAX_NAME_SIZE)
    description = models.TextField(null=True)

    def __unicode__(self):
        return self.title
