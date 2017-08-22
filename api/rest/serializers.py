from django.contrib.auth.models import User
from rest_framework import serializers

from ..models import Notebook, Note, Task
from .fields import SecondaryKeyRelatedField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'date_joined', 'last_login', 'first_name', 'last_name', 'email')


class NotebookSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source='ext_id', format='hex')
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Notebook
        fields = ('id', 'user', 'created', 'updated', 'name')


class NoteSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source='ext_id', format='hex')
    notebook = SecondaryKeyRelatedField(read_only=True)

    class Meta:
        model = Note
        fields = ('id', 'notebook', 'created', 'updated', 'title', 'text')


class TaskSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source='ext_id', format='hex')
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'user', 'created', 'updated', 'done', 'title', 'description')
