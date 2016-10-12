from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_nested import relations

from .models import Notebook, Note, Task


class UserSerializer(serializers.HyperlinkedModelSerializer):
    notebooks = relations.NestedHyperlinkedRelatedField(many=True, read_only=True, source='notebook_set',
                                                        view_name='notebook-detail', parent_lookup_field='user',
                                                        parent_lookup_url_kwarg='user_pk')
    tasks = relations.NestedHyperlinkedRelatedField(many=True, read_only=True, source='task_set',
                                                    view_name='task-detail', parent_lookup_field='user',
                                                    parent_lookup_url_kwarg='user_pk')

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'notebooks', 'tasks')


class NotebookSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
    notes = relations.NestedHyperlinkedRelatedField(many=True, read_only=True, source='note_set',
                                                    view_name='note-detail', parent_lookup_field='notebook',
                                                    parent_lookup_url_kwarg='notebook_pk')

    class Meta:
        model = Notebook
        fields = ('url', 'user', 'name', 'notes')


class NoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Note
        fields = ('url', 'notebook', 'title', 'text')


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')

    class Meta:
        model = Task
        fields = ('url', 'user', 'done', 'title', 'description')
