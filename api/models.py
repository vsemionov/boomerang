from __future__ import unicode_literals

from django.db import models

# Create your models here.

MAX_NAME_SIZE = 128
MAX_TEXT_SIZE = 32 * 1024

class Notebook(models.Model):
    user = models.ForeignKey("auth.User")
    name = models.CharField(max_length=MAX_NAME_SIZE)


class Note(models.Model):
    notebook = models.ForeignKey(Notebook)
    title = models.CharField(max_length=MAX_NAME_SIZE)
    text = models.TextField(max_length=MAX_TEXT_SIZE)


class Task(models.Model):
    user = models.ForeignKey("auth.User")
    done = models.BooleanField(default=False)
    title = models.CharField(max_length=MAX_NAME_SIZE)
    description = models.TextField(max_length=MAX_TEXT_SIZE)
