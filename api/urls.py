from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'notebooks', views.NotebookViewSet)
router.register(r'notes', views.NoteViewSet)
router.register(r'tasks', views.TaskViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^info', views.info),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
]
