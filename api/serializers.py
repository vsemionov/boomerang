from rest_framework import serializers

from .models import Notebook, Note, Task


class NotebookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notebook


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
