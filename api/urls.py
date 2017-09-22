from django.conf.urls import url, include
from rest_framework_nested import routers

from . import views, info, token, jwt


root_router = routers.DefaultRouter()
root_router.include_format_suffixes = False
root_router.register(r'users', views.UserViewSet)

user_router = routers.NestedSimpleRouter(root_router, r'users', lookup='user')
user_router.register(r'notebooks', views.NotebookViewSet)
user_router.register(r'notes', views.UserNoteViewSet)
user_router.register(r'tasks', views.TaskViewSet)

notebook_router = routers.NestedSimpleRouter(user_router, r'notebooks', lookup='notebook')
notebook_router.register(r'notes', views.NoteViewSet)

root_router.register(r'info', info.ApiInfoViewSet, base_name='info')
root_router.register(r'token', token.TokenViewSet, base_name='token')
root_router.register(r'jwt', jwt.JWTViewSet, base_name='jwt')

urlpatterns = [
    url(r'^', include(root_router.urls)),
    url(r'^', include(user_router.urls)),
    url(r'^', include(notebook_router.urls)),
]
