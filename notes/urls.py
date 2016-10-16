"""notes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from django.views.generic.base import RedirectView


def redirect_view(view_name, query=False):
    return RedirectView.as_view(pattern_name=view_name, query_string=query)

auth_urls = [
    url(r'^login/$', redirect_view('account_login', query=True), name='login'),
    url(r'^logout/$', redirect_view('account_logout', query=True), name='logout'),
]

urlpatterns = [
    url(r'^$', redirect_view('api-root'), name='index'),
    url(r'^api/', include('api.urls')),
    url(r'^auth/', include(auth_urls, namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
]


from django.conf import settings

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
