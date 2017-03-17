from django.views.generic.base import TemplateView
from django.views.generic.dates import DayArchiveView, TodayArchiveView
from django.db.models import Q
from django.views.generic.list import ListView

from scheduler_core.models import MovieSchedule, BroadcastCompany


# Create your views here.
# Schedule for a day.
class MovieScheduleDAV(DayArchiveView):
    model = MovieSchedule
    date_field = 'start_time'
    allow_future = True

    def get_context_data(self, **kwargs):
        context = super(MovieScheduleDAV, self).get_context_data(**kwargs)

        # Broadcasting company.
        bc_list = BroadcastCompany.objects.all()
        context['bc_list'] = bc_list

        # Schedule for hours.
        _, all_programs, _ = self.get_dated_items()         # Get schedules of certain day.
        programs_all = []
        for i in range(24):
            programs_hour = all_programs.filter(start_time__hour=i)

            # Get schedules for every broadcasting companies on this time.
            programs = []
            for j in range(bc_list.count()):
                programs.append({
                    "company_id": bc_list[j].id,
                    "program_list": programs_hour.filter(Q(broadcast_company=bc_list[j])).order_by('start_time')
                })
            programs_all.append({"hour": i, "programs": programs})

        context['programs_all'] = programs_all

        return context


# Today's Schedule View.
class MovieScheduleTAV(MovieScheduleDAV, TodayArchiveView):
    model = MovieSchedule
    date_field = 'start_time'
    allow_future = True


# License
class LicenseTemplateView(TemplateView):
    template_name = "scheduler_core/license.html"


# Setting whether displaying or hiding some broadcast company's schedule.
class BroadcastCompanyDisplaySettingView(ListView):
    model = BroadcastCompany
