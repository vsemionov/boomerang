from __future__ import unicode_literals

import uuid
from django.db import models
from django.utils import timezone


# Create your models here.

MAX_NAME_SIZE = 128
MAX_TEXT_SIZE = 32*1024


class Notebook(models.Model):
    ext_id = models.UUIDField(unique=True, null=False, default=uuid.uuid4)
    user = models.ForeignKey('auth.User', to_field='username')

    screated = models.DateTimeField(auto_now_add=True)
    supdated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)

    name = models.CharField(max_length=MAX_NAME_SIZE)

    def __unicode__(self):
        return self.name


class Note(models.Model):
    ext_id = models.UUIDField(unique=True, null=False, default=uuid.uuid4)
    notebook = models.ForeignKey(Notebook, to_field='ext_id')

    screated = models.DateTimeField(auto_now_add=True)
    supdated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)

    title = models.CharField(max_length=MAX_NAME_SIZE)
    text = models.TextField(max_length=MAX_TEXT_SIZE)

    def __unicode__(self):
        return self.title


class Task(models.Model):
    ext_id = models.UUIDField(unique=True, null=False, default=uuid.uuid4)
    user = models.ForeignKey('auth.User', to_field='username')

    screated = models.DateTimeField(auto_now_add=True)
    supdated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)

    done = models.BooleanField(default=False)
    title = models.CharField(max_length=MAX_NAME_SIZE)
    description = models.TextField(null=True, max_length=MAX_TEXT_SIZE)

    def __unicode__(self):
        return self.title
