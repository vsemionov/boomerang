import uuid

from django.db import models
from rest_offline.models import TrackedModel


MAX_NAME_SIZE = 128
MAX_TEXT_SIZE = 32*1024


class Notebook(TrackedModel):
    ext_id = models.UUIDField(unique=True, null=False, default=uuid.uuid4)
    user = models.ForeignKey('auth.User', to_field='username')

    name = models.CharField(max_length=MAX_NAME_SIZE)

    def __str__(self):
        return self.name


class Note(TrackedModel):
    ext_id = models.UUIDField(unique=True, null=False, default=uuid.uuid4)
    notebook = models.ForeignKey(Notebook, to_field='ext_id')

    title = models.CharField(max_length=MAX_NAME_SIZE)
    text = models.TextField(max_length=MAX_TEXT_SIZE)

    def __str__(self):
        return self.title


class Task(TrackedModel):
    ext_id = models.UUIDField(unique=True, null=False, default=uuid.uuid4)
    user = models.ForeignKey('auth.User', to_field='username')

    done = models.BooleanField(default=False)
    title = models.CharField(max_length=MAX_NAME_SIZE)
    description = models.TextField(null=True, max_length=MAX_TEXT_SIZE)

    def __str__(self):
        return self.title
