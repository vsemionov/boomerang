from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_nested import relations

from .models import Notebook, Note, Task


class NestedHyperlinkedIdentityField(relations.NestedHyperlinkedRelatedField):
    def __init__(self, view_name=None, *args, **kwargs):
        assert view_name is not None, 'The `view_name` argument is required.'
        kwargs['read_only'] = True
        kwargs['source'] = '*'
        super(NestedHyperlinkedIdentityField, self).__init__(view_name, *args, **kwargs)

    def use_pk_only_optimization(self):
        return False


class FullyNestedHyperlinkedRelatedField(relations.NestedHyperlinkedRelatedField):
    def __init__(self, *args, **kwargs):
        self.parent_lookup_fields = kwargs.pop('parent_lookup_fields', (self.parent_lookup_field,))
        self.parent_lookup_url_kwargs = kwargs.pop('parent_lookup_url_kwargs',
                                                   (self.parent_lookup_field,) * len(self.parent_lookup_fields))
        self.parent_lookup_related_fields = kwargs.pop('parent_lookup_related_fields',
                                                       (self.parent_lookup_related_field,) * len(
                                                           self.parent_lookup_fields))
        super(FullyNestedHyperlinkedRelatedField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        if hasattr(obj, 'pk') and obj.pk is None:
            return None

        kwargs = {}
        lookup_value = getattr(obj, self.lookup_field)
        kwargs[self.lookup_url_kwarg] = lookup_value

        for (parent_lookup_field, parent_lookup_url_kwarg, parent_lookup_related_field) in \
                zip(self.parent_lookup_fields, self.parent_lookup_url_kwargs, self.parent_lookup_related_fields):
            if obj is not None:
                parent_lookup_object = getattr(obj, parent_lookup_field)
                parent_lookup_value = getattr(
                    parent_lookup_object,
                    parent_lookup_related_field
                ) if parent_lookup_object else None
            else:
                parent_lookup_object = None
                parent_lookup_value = None

            kwargs[parent_lookup_url_kwarg] = parent_lookup_value

            obj = parent_lookup_object

        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)


class FullyNestedHyperlinkedIdentityField(FullyNestedHyperlinkedRelatedField):
    def __init__(self, view_name=None, *args, **kwargs):
        assert view_name is not None, 'The `view_name` argument is required.'
        kwargs['read_only'] = True
        kwargs['source'] = '*'
        super(FullyNestedHyperlinkedIdentityField, self).__init__(view_name, *args, **kwargs)

    def use_pk_only_optimization(self):
        return False


class UserLinksSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name='user-detail')
    notebooks = serializers.HyperlinkedIdentityField(view_name='notebook-list', lookup_url_kwarg='user_pk')
    tasks = serializers.HyperlinkedIdentityField(view_name='task-list', lookup_url_kwarg='user_pk')

    class Meta:
        model = User
        fields = ('self', 'notebooks', 'tasks')


class UserSerializer(serializers.ModelSerializer):
    notebooks = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='notebook_set')
    tasks = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='task_set')
    links = UserLinksSerializer(read_only=True, source='*')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'notebooks', 'tasks', 'links')


class NotebookLinksSerializer(serializers.ModelSerializer):
    self = NestedHyperlinkedIdentityField(view_name='notebook-detail',
                                          parent_lookup_field='user', parent_lookup_url_kwarg='user_pk')
    user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
    notes = FullyNestedHyperlinkedIdentityField(view_name='note-list', lookup_url_kwarg='notebook_pk',
                                                parent_lookup_fields=('user',), parent_lookup_url_kwargs=('user_pk',))

    class Meta:
        model = Notebook
        fields = ('self', 'user', 'notes')


class NotebookSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    notes = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='note_set')
    links = NotebookLinksSerializer(read_only=True, source='*')

    class Meta:
        model = Notebook
        fields = ('id', 'user', 'name', 'notes', 'links')


class NoteLinksSerializer(serializers.ModelSerializer):
    self = FullyNestedHyperlinkedRelatedField(read_only=True, source='*', view_name='note-detail',
                                              parent_lookup_fields=('notebook', 'user'),
                                              parent_lookup_url_kwargs=('notebook_pk', 'user_pk'))
    notebook = relations.NestedHyperlinkedRelatedField(read_only=True, view_name='notebook-detail',
                                                       parent_lookup_field='user', parent_lookup_url_kwarg='user_pk')

    class Meta:
        model = Note
        fields = ('self', 'notebook')


class NoteSerializer(serializers.ModelSerializer):
    links = NoteLinksSerializer(read_only=True, source='*')

    class Meta:
        model = Note
        fields = ('id', 'notebook', 'title', 'text', 'links')


class TaskLinksSerializer(serializers.ModelSerializer):
    self = relations.NestedHyperlinkedRelatedField(read_only=True, source='*', view_name='task-detail',
                                                   parent_lookup_field='user', parent_lookup_url_kwarg='user_pk')
    user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')

    class Meta:
        model = Task
        fields = ('self', 'user')


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    links = TaskLinksSerializer(read_only=True, source='*')

    class Meta:
        model = Task
        fields = ('id', 'user', 'done', 'title', 'description', 'links')
