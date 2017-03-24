from django.contrib import admin

from .models import BroadcastCompany, MovieSchedule, LatestUpdate


# MovieScheduleAdmin
class MovieScheduleAdmin(admin.ModelAdmin):
    list_display = ("broadcast_company", "title", "start_time", "end_time", "ratings")


# LatestUpdateAdmin
class LatestUpdateAdmin(admin.ModelAdmin):
    list_display = ("broadcast_company", "latest_update")

# Register your models here.
admin.site.register(MovieSchedule, MovieScheduleAdmin)
admin.site.register(LatestUpdate, LatestUpdateAdmin)
admin.site.register(BroadcastCompany)
