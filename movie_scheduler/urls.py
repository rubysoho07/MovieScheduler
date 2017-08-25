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
from django.conf.urls import url, include
from django.contrib import admin
from scheduler_core import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'schedules', views.MovieScheduleViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.MovieScheduleDAV.as_view(), name='day'),
    url(r'^$', views.MovieScheduleTAV.as_view(), name='today_schedule'),
    url(r'^license/$', views.LicenseTemplateView.as_view(), name='license'),
    url(r'^setting/$', views.BroadcastCompanyDisplaySettingView.as_view(), name='setting'),

    url(r'^broadcast/(?P<pk>\d+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        views.BroadcastDailyScheduleDAV.as_view(), name='daily_schedule'),
    url(r'^broadcast/all/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        views.AllBroadcastDailyScheduleDAV.as_view(), name='daily_schedule'),

    url(r'^broadcast/today/(?P<pk>\d+)/$', views.BroadcastTodayScheduleView.as_view(), name='today_schedule'),
    url(r'^broadcast/today/all/$', views.AllBroadcastTodayScheduleView.as_view(), name='today_all_schedule'),

    url(r'^api/', include(router.urls)),
]
