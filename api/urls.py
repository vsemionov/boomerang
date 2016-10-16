from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'notebooks', views.NotebookViewSet)
router.register(r'notes', views.NoteViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'info', views.InfoViewSet, base_name='info')

urlpatterns = [
    url(r'^', include(router.urls)),
]
