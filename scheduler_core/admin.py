from django.contrib import admin

from .models import MovieSchedule


# MovieScheduleAdmin
class MovieScheduleAdmin(admin.ModelAdmin):
    list_display = ("broadcast_company", "title", "start_time", "end_time", "ratings")

# Register your models here.
admin.site.register(MovieSchedule, MovieScheduleAdmin)
