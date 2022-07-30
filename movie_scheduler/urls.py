"""movie_scheduler URL Configuration"""
from django.urls import re_path
from django.contrib import admin
from scheduler_core import views

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.MovieScheduleDAV.as_view(), name='day'),
    re_path(r'^$', views.MovieScheduleTAV.as_view(), name='today_schedule'),
    re_path(r'^license/$', views.LicenseTemplateView.as_view(), name='license'),
    re_path(r'^setting/$', views.BroadcastCompanyDisplaySettingView.as_view(), name='setting'),

    re_path(r'^broadcast/(?P<pk>\d+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
            views.BroadcastDailyScheduleDAV.as_view(), name='daily_schedule'),
    re_path(r'^broadcast/all/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
            views.AllBroadcastDailyScheduleDAV.as_view(), name='daily_schedule'),

    re_path(r'^broadcast/today/(?P<pk>\d+)/$', views.BroadcastTodayScheduleView.as_view(), name='today_schedule'),
    re_path(r'^broadcast/today/all/$', views.AllBroadcastTodayScheduleView.as_view(), name='today_all_schedule'),
]
