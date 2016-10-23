from __future__ import unicode_literals

import uuid
from django.db import models

# Create your models here.

MAX_NAME_SIZE = 128


class Notebook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey('auth.User', to_field='username')
    name = models.CharField(max_length=MAX_NAME_SIZE)

    def __unicode__(self):
        return self.name


class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    notebook = models.ForeignKey(Notebook)
    title = models.CharField(max_length=MAX_NAME_SIZE)
    text = models.TextField()

    def __unicode__(self):
        return self.title


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey('auth.User', to_field='username')
    done = models.BooleanField(default=False)
    title = models.CharField(max_length=MAX_NAME_SIZE)
    description = models.TextField(null=True)

    def __unicode__(self):
        return self.title
