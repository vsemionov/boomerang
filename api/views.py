# from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets

from .models import Notebook, Note, Task
from .serializers import NotebookSerializer, NoteSerializer, TaskSerializer


class NotebookViewSet(viewsets.ModelViewSet):
    queryset = Notebook.objects.all()
    serializer_class = NotebookSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
