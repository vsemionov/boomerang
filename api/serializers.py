import uuid

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Notebook, Note, Task


class SecondaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, *args, **kwargs):
        kwargs['pk_field'] = serializers.UUIDField(format='hex')
        super(SecondaryKeyRelatedField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.ext_id)
        return value.ext_id


class DynamicHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    def __init__(self, parent_lookup=None, aux_lookup=None, *args, **kwargs):
        self.parent_lookup = parent_lookup or {}
        self.aux_lookup = aux_lookup or {}
        super(DynamicHyperlinkedIdentityField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        kwargs.update(self.parent_lookup)
        kwargs.update({kwarg: getattr(obj, field) for (kwarg, field) in self.aux_lookup.iteritems()})

        for key in kwargs:
            value = kwargs[key]
            if isinstance(value, uuid.UUID):
                kwargs[key] = value.hex

        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)


User.get_active_notebooks = lambda self: self.notebook_set.filter(deleted=False)
User.get_active_tasks = lambda self: self.task_set.filter(deleted=False)
Notebook.get_active_notes = lambda self: self.note_set.filter(deleted=False)


class UserSerializer(serializers.ModelSerializer):
    notebooks = SecondaryKeyRelatedField(read_only=True, many=True, source='get_active_notebooks')
    tasks = SecondaryKeyRelatedField(read_only=True, many=True, source='get_active_tasks')

    class Meta:
        model = User
        fields = ('username', 'date_joined', 'last_login', 'first_name', 'last_name', 'email', 'notebooks', 'tasks')


class NotebookSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source='ext_id', format='hex')
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    notes = SecondaryKeyRelatedField(read_only=True, many=True, source='get_active_notes')

    class Meta:
        model = Notebook
        fields = ('id', 'user', 'created', 'updated', 'name', 'notes')


class NoteSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source='ext_id', format='hex')
    notebook = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Note
        fields = ('id', 'notebook', 'created', 'updated', 'title', 'text')


class TaskSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source='ext_id', format='hex')
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'user', 'created', 'updated', 'done', 'title', 'description')


def get_dynamic_user_serializer():
    class UserLinksSerializer(serializers.Serializer):
        self = DynamicHyperlinkedIdentityField(view_name='user-detail',
                                               lookup_field='username')
        notebooks = DynamicHyperlinkedIdentityField(view_name='notebook-list',
                                                    lookup_url_kwarg='user_username', lookup_field='username')
        notes = DynamicHyperlinkedIdentityField(view_name='user-notes',
                                                lookup_field='username')
        tasks = DynamicHyperlinkedIdentityField(view_name='task-list',
                                                lookup_url_kwarg='user_username', lookup_field='username')

    class DynamicUserSerializer(UserSerializer):
        links = UserLinksSerializer(read_only=True, source='*')

        class Meta(UserSerializer.Meta):
            fields = UserSerializer.Meta.fields + ('links',)

    return DynamicUserSerializer


def get_hyperlinked_notebook_serializer_class(user_username):
    class NotebookLinksSerializer(serializers.Serializer):
        self = DynamicHyperlinkedIdentityField(view_name='notebook-detail',
                                               lookup_field='ext_id',
                                               parent_lookup=dict(user_username=user_username))
        user = DynamicHyperlinkedIdentityField(view_name='user-detail',
                                               lookup_url_kwarg='username', lookup_field='user_id')
        notes = DynamicHyperlinkedIdentityField(view_name='note-list',
                                                lookup_url_kwarg='notebook_ext_id', lookup_field='ext_id',
                                                parent_lookup=dict(user_username=user_username))

    class DynamicNotebookSerializer(NotebookSerializer):
        links = NotebookLinksSerializer(read_only=True, source='*')

        class Meta(NotebookSerializer.Meta):
            fields = NotebookSerializer.Meta.fields + ('links',)

    return DynamicNotebookSerializer


def get_hyperlinked_note_serializer_class(user_username):
    class NoteLinksSerializer(serializers.Serializer):
        self = DynamicHyperlinkedIdentityField(view_name='note-detail',
                                               lookup_field='ext_id',
                                               parent_lookup=dict(user_username=user_username),
                                               aux_lookup=dict(notebook_ext_id='notebook_id'))
        notebook = DynamicHyperlinkedIdentityField(view_name='notebook-detail',
                                                   lookup_url_kwarg='ext_id', lookup_field='notebook_id',
                                                   parent_lookup=dict(user_username=user_username))

    class DynamicNoteSerializer(NoteSerializer):
        links = NoteLinksSerializer(read_only=True, source='*')

        class Meta(NoteSerializer.Meta):
            fields = NoteSerializer.Meta.fields + ('links',)

    return DynamicNoteSerializer


def get_hyperlinked_task_serializer_class(user_username):
    class TaskLinksSerializer(serializers.Serializer):
        self = DynamicHyperlinkedIdentityField(view_name='task-detail',
                                               lookup_field='ext_id',
                                               parent_lookup=dict(user_username=user_username))
        user = DynamicHyperlinkedIdentityField(view_name='user-detail',
                                               lookup_url_kwarg='username', lookup_field='user_id')

    class DynamicTaskSerializer(TaskSerializer):
        links = TaskLinksSerializer(read_only=True, source='*')

        class Meta(TaskSerializer.Meta):
            fields = TaskSerializer.Meta.fields + ('links',)

    return DynamicTaskSerializer
