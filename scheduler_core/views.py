from django.views.generic.base import TemplateView
from django.views.generic.dates import DayArchiveView, TodayArchiveView
from django.db.models import Q

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
        programs_hour = []
        for i in range(24):
            programs = all_programs.filter(start_time__hour=i)

            # For every broadcasting companies.
            programs_list = []
            for j in range(bc_list.count()):
                programs_list.append(programs.filter(Q(broadcast_company=bc_list[j])).order_by('start_time'))
            programs_hour.append({"hour": i, "programs_list": programs_list})

        context['programs_hour'] = programs_hour

        return context


# Today's Schedule View.
class MovieScheduleTAV(MovieScheduleDAV, TodayArchiveView):
    model = MovieSchedule
    date_field = 'start_time'
    allow_future = True


# License
class LicenseTemplateView(TemplateView):
    template_name = "scheduler_core/license.html"
