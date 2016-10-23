from __future__ import unicode_literals

import uuid
from django.db import models

# Create your models here.

MAX_NAME_SIZE = 128


class Notebook(models.Model):
    ext_id = models.UUIDField(unique=True, null=False, default=uuid.uuid4)
    user = models.ForeignKey('auth.User', to_field='username')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=MAX_NAME_SIZE)

    def __unicode__(self):
        return self.name


class Note(models.Model):
    ext_id = models.UUIDField(unique=True, null=False, default=uuid.uuid4)
    notebook = models.ForeignKey(Notebook, to_field='ext_id')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=MAX_NAME_SIZE)
    text = models.TextField()

    def __unicode__(self):
        return self.title


class Task(models.Model):
    ext_id = models.UUIDField(unique=True, null=False, default=uuid.uuid4)
    user = models.ForeignKey('auth.User', to_field='username')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    done = models.BooleanField(default=False)
    title = models.CharField(max_length=MAX_NAME_SIZE)
    description = models.TextField(null=True)

    def __unicode__(self):
        return self.title
