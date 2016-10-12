from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Notebook, Note, Task


class UserSerializer(serializers.HyperlinkedModelSerializer):
    notebooks = serializers.HyperlinkedRelatedField(many=True, source='notebook_set', view_name='notebook-detail',
                                                    read_only=True)
    tasks = serializers.HyperlinkedRelatedField(many=True, source='task_set', view_name='task-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'notebooks', 'tasks')


class NotebookSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    notes = serializers.HyperlinkedRelatedField(many=True, source='note_set', view_name='note-detail', read_only=True)

    class Meta:
        model = Notebook
        fields = ('url', 'user', 'name', 'notes')


class NoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Note
        fields = ('url', 'notebook', 'title', 'text')


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)

    class Meta:
        model = Task
        fields = ('url', 'user', 'done', 'title', 'description')
