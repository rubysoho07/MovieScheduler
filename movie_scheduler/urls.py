"""movie_scheduler URL Configuration

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
from django.conf.urls import url
from django.contrib import admin
from scheduler_core.views import MovieScheduleDAV, MovieScheduleTAV

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/$', MovieScheduleDAV.as_view(), name='day'),
    url(r'^$', MovieScheduleTAV.as_view(), name='today_schedule'),
]
