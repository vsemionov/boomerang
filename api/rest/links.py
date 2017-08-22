from rest_framework import serializers

from .fields import SecondaryKeyRelatedField, DynamicHyperlinkedIdentityField
from .serializers import UserSerializer, NotebookSerializer, NoteSerializer, TaskSerializer


class UserLinksSerializer(serializers.Serializer):
    self = DynamicHyperlinkedIdentityField(view_name='user-detail',
                                           lookup_field='username')
    notebooks = DynamicHyperlinkedIdentityField(view_name='notebook-list',
                                                lookup_url_kwarg='user_username', lookup_field='username')
    tasks = DynamicHyperlinkedIdentityField(view_name='task-list',
                                            lookup_url_kwarg='user_username', lookup_field='username')

class HyperlinkedUserSerializer(UserSerializer):
    links = UserLinksSerializer(read_only=True, source='*')

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('links',)


def create_hyperlinked_notebook_serializer_class(user_username):
    class NotebookLinksSerializer(serializers.Serializer):
        self = DynamicHyperlinkedIdentityField(view_name='notebook-detail',
                                               lookup_field='ext_id',
                                               parent_lookup=dict(user_username=user_username))
        user = DynamicHyperlinkedIdentityField(view_name='user-detail',
                                               lookup_url_kwarg='username', lookup_field='user_id')
        notes = DynamicHyperlinkedIdentityField(view_name='note-list',
                                                lookup_url_kwarg='notebook_ext_id', lookup_field='ext_id',
                                                parent_lookup=dict(user_username=user_username))

    class HyperlinkedNotebookSerializer(NotebookSerializer):
        links = NotebookLinksSerializer(read_only=True, source='*')

        class Meta(NotebookSerializer.Meta):
            fields = NotebookSerializer.Meta.fields + ('links',)

    return HyperlinkedNotebookSerializer


def create_hyperlinked_note_serializer_class(user_username, notebooks=None):
    class NoteLinksSerializer(serializers.Serializer):
        self = DynamicHyperlinkedIdentityField(view_name='note-detail',
                                               lookup_field='ext_id',
                                               parent_lookup=dict(user_username=user_username),
                                               aux_lookup=dict(notebook_ext_id='notebook_id'))
        notebook = DynamicHyperlinkedIdentityField(view_name='notebook-detail',
                                                   lookup_url_kwarg='ext_id', lookup_field='notebook_id',
                                                   parent_lookup=dict(user_username=user_username))

    class HyperlinkedNoteSerializer(NoteSerializer):
        if notebooks is not None:
            notebook = SecondaryKeyRelatedField(queryset=notebooks)

        links = NoteLinksSerializer(read_only=True, source='*')

        class Meta(NoteSerializer.Meta):
            fields = NoteSerializer.Meta.fields + ('links',)

    return HyperlinkedNoteSerializer


def create_hyperlinked_task_serializer_class(user_username):
    class TaskLinksSerializer(serializers.Serializer):
        self = DynamicHyperlinkedIdentityField(view_name='task-detail',
                                               lookup_field='ext_id',
                                               parent_lookup=dict(user_username=user_username))
        user = DynamicHyperlinkedIdentityField(view_name='user-detail',
                                               lookup_url_kwarg='username', lookup_field='user_id')

    class HyperlinkedTaskSerializer(TaskSerializer):
        links = TaskLinksSerializer(read_only=True, source='*')

        class Meta(TaskSerializer.Meta):
            fields = TaskSerializer.Meta.fields + ('links',)

    return HyperlinkedTaskSerializer
