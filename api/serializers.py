from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Notebook, Note, Task


class DynamicHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    def __init__(self, parent_lookup=None, *args, **kwargs):
        self.parent_lookup = parent_lookup or {}
        super(DynamicHyperlinkedIdentityField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        kwargs.update(self.parent_lookup)
        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)


class UserSerializer(serializers.ModelSerializer):
    notebooks = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='notebook_set')
    tasks = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='task_set')

    class Meta:
        model = User
        fields = ('username', 'email', 'notebooks', 'tasks')


class NotebookSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source='ext_id')
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    notes = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='note_set')

    class Meta:
        model = Notebook
        fields = ('id', 'user', 'name', 'notes')


class NoteSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source='ext_id')
    notebook = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Note
        fields = ('id', 'notebook', 'title', 'text')


class TaskSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source='ext_id')
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'user', 'done', 'title', 'description')


def get_dynamic_user_serializer():
    class UserLinksSerializer(serializers.Serializer):
        self = DynamicHyperlinkedIdentityField(view_name='user-detail',
                                               lookup_field='username')
        notebooks = DynamicHyperlinkedIdentityField(view_name='notebook-list',
                                                    lookup_field='username', lookup_url_kwarg='user_username')
        tasks = DynamicHyperlinkedIdentityField(view_name='task-list',
                                                lookup_field='username', lookup_url_kwarg='user_username')

    class DynamicUserSerializer(UserSerializer):
        links = UserLinksSerializer(read_only=True, source='*')

        class Meta(UserSerializer.Meta):
            fields = UserSerializer.Meta.fields + ('links',)

    return DynamicUserSerializer


def get_dynamic_notebook_serializer(view_kwargs):
    class NotebookLinksSerializer(serializers.Serializer):
        self = DynamicHyperlinkedIdentityField(view_name='notebook-detail',
                                               lookup_field='ext_id',
                                               parent_lookup=dict(user_username=view_kwargs['user_username']))
        user = DynamicHyperlinkedIdentityField(view_name='user-detail',
                                               lookup_field='user_id', lookup_url_kwarg='username')
        notes = DynamicHyperlinkedIdentityField(view_name='note-list',
                                                lookup_field='ext_id', lookup_url_kwarg='notebook_ext_id',
                                                parent_lookup=dict(user_username=view_kwargs['user_username']))

    class DynamicNotebookSerializer(NotebookSerializer):
        links = NotebookLinksSerializer(read_only=True, source='*')

        class Meta(NotebookSerializer.Meta):
            fields = NotebookSerializer.Meta.fields + ('links',)

    return DynamicNotebookSerializer


def get_dynamic_note_serializer(view_kwargs):
    class NoteLinksSerializer(serializers.Serializer):
        self = DynamicHyperlinkedIdentityField(view_name='note-detail',
                                               lookup_field='ext_id',
                                               parent_lookup=dict(user_username=view_kwargs['user_username'],
                                                                  notebook_ext_id=view_kwargs['notebook_ext_id']))
        notebook = DynamicHyperlinkedIdentityField(view_name='notebook-detail',
                                                   lookup_field='notebook_id', lookup_url_kwarg='ext_id',
                                                   parent_lookup=dict(user_username=view_kwargs['user_username']))

    class DynamicNoteSerializer(NoteSerializer):
        links = NoteLinksSerializer(read_only=True, source='*')

        class Meta(NoteSerializer.Meta):
            fields = NoteSerializer.Meta.fields + ('links',)

    return DynamicNoteSerializer


def get_dynamic_task_serializer(view_kwargs):
    class TaskLinksSerializer(serializers.Serializer):
        self = DynamicHyperlinkedIdentityField(view_name='task-detail',
                                               lookup_field='ext_id',
                                               parent_lookup=dict(user_username=view_kwargs['user_username']))
        user = DynamicHyperlinkedIdentityField(view_name='user-detail',
                                               lookup_field='user_id', lookup_url_kwarg='username')

    class DynamicTaskSerializer(TaskSerializer):
        links = TaskLinksSerializer(read_only=True, source='*')

        class Meta(TaskSerializer.Meta):
            fields = TaskSerializer.Meta.fields + ('links',)

    return DynamicTaskSerializer
