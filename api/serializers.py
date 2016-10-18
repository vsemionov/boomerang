from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Notebook, Note, Task


class UserLinksSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name='user-detail')
    notebooks = serializers.HyperlinkedRelatedField(read_only=True, many=True, source='notebook_set',
                                                    view_name='notebook-detail')
    tasks = serializers.HyperlinkedRelatedField(read_only=True, many=True, source='task_set', view_name='task-detail')

    class Meta:
        model = User
        fields = ('self', 'notebooks', 'tasks')


class UserSerializer(serializers.ModelSerializer):
    notebooks = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='notebook_set')
    tasks = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='task_set')
    # links = UserLinksSerializer(read_only=True, source='*')

    class Meta:
        model = User
        # fields = ('id', 'username', 'email', 'notebooks', 'tasks', 'links')
        fields = ('id', 'username', 'email', 'notebooks', 'tasks')


class NotebookLinksSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name='notebook-detail')
    user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
    notes = serializers.HyperlinkedRelatedField(read_only=True, many=True, source='note_set', view_name='note-detail')

    class Meta:
        model = Notebook
        fields = ('self', 'user', 'notes')


class NotebookSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    notes = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='note_set')
    # links = NotebookLinksSerializer(read_only=True, source='*')

    class Meta:
        model = Notebook
        # fields = ('id', 'user', 'name', 'notes', 'links')
        fields = ('id', 'user', 'name', 'notes')


class NoteLinksSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name='note-detail')
    notebook = serializers.HyperlinkedRelatedField(read_only=True, view_name='notebook-detail')

    class Meta:
        model = Note
        fields = ('self', 'notebook')


class NoteSerializer(serializers.ModelSerializer):
    # links = NoteLinksSerializer(read_only=True, source='*')

    class Meta:
        model = Note
        # fields = ('id', 'notebook', 'title', 'text', 'links')
        fields = ('id', 'notebook', 'title', 'text')


class TaskLinksSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name='task-detail')
    user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')

    class Meta:
        model = Task
        fields = ('self', 'user')


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    # links = TaskLinksSerializer(read_only=True, source='*')

    class Meta:
        model = Task
        # fields = ('id', 'user', 'done', 'title', 'description', 'links')
        fields = ('id', 'user', 'done', 'title', 'description')
