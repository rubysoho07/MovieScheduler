from django.views.generic.base import TemplateView
from django.views.generic.dates import DayArchiveView, TodayArchiveView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404

from django.db.models import Q

from django.http import JsonResponse

from scheduler_core.models import MovieSchedule, BroadcastCompany

from rest_framework import generics
from rest_framework.response import Response
from scheduler_core.serializers import MovieScheduleSerializer


# Create your views here.
class MovieScheduleDAV(DayArchiveView):
    """Display schedule for a day."""

    model = MovieSchedule
    date_field = 'start_time'
    allow_future = True
    month_format = "%m"

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

        context['hours'] = range(24)

        return context


class MovieScheduleTAV(MovieScheduleDAV, TodayArchiveView):
    """Display today's schedule."""

    model = MovieSchedule
    date_field = 'start_time'
    allow_future = True


class LicenseTemplateView(TemplateView):
    """Show license information of external libraries."""

    template_name = "scheduler_core/license.html"


class BroadcastCompanyDisplaySettingView(ListView):
    """Set whether displaying or hiding some broadcast company's schedule."""

    model = BroadcastCompany


class JSONResponseMixin(object):
    """A mixin that can be used to render a JSON response. (From Django Documentation)"""

    def render_to_json_response(self, context, **response_kwargs):
        """Returns a JSON response, transforming 'context' to make the payload."""
        return JsonResponse(
            self.get_data(context),
            json_dumps_params={'ensure_ascii': False},
            safe=False,
            **response_kwargs
        )

    def get_data(self, context):
        """Returns an object that will be serialized as JSON by json.dumps()."""
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context


class BroadcastDailyScheduleDAV(JSONResponseMixin, DayArchiveView):
    """One day's movie schedule of a broadcast company from database in JSON."""

    model = MovieSchedule
    date_field = 'start_time'
    allow_future = True
    month_format = "%m"

    def render_to_response(self, context, **response_kwargs):
        """Override render_to_response method from TemplateResponseMixin class to return JSON data."""
        return self.render_to_json_response(context, **response_kwargs)

    def get_data(self, context):
        """Make schedule data from database and return it."""
        broadcast_company = BroadcastCompany.objects.get(id=self.kwargs['pk'])
        _, dated_schedule_queryset, _ = self.get_dated_items()
        dated_schedule = dated_schedule_queryset.filter(broadcast_company=broadcast_company)
        schedule = list([] for _ in range(24))

        for item in dated_schedule:
            schedule[item.start_time.hour].append({
                'title': item.title.replace('\r\n', ''),
                'start_time': item.start_time,
                'ratings': item.ratings
            })

        data = {
            'broadcast_company': broadcast_company.bc_name,
            'dated_schedule': schedule
        }

        return data


class BroadcastTodayScheduleView(BroadcastDailyScheduleDAV, TodayArchiveView):
    """Today's movie schedule of a broadcast company from database in JSON."""

    model = MovieSchedule
    date_field = 'start_time'
    allow_future = True


class AllBroadcastDailyScheduleDAV(JSONResponseMixin, DayArchiveView):
    """All movie schedule of a day from database in JSON."""
    model = MovieSchedule
    date_field = 'start_time'
    allow_future = True
    month_format = "%m"

    def render_to_response(self, context, **response_kwargs):
        """Override render_to_response method from TemplateResponseMixin class to return JSON data."""
        return self.render_to_json_response(context, **response_kwargs)

    def get_data(self, context):
        """Make schedule data from database and return it."""
        broadcast_company = BroadcastCompany.objects.all()
        _, dated_schedule_queryset, _ = self.get_dated_items()
        data = list()

        for company in broadcast_company:
            schedule = list([] for _ in range(24))
            dated_schedule = dated_schedule_queryset.filter(broadcast_company=company)

            for item in dated_schedule:
                schedule[item.start_time.hour].append({
                    'title': item.title.replace('\r\n', ''),
                    'start_time': item.start_time,
                    'ratings': item.ratings
                })

            data.append({
                'broadcast_company': company.bc_name,
                'dated_schedule': schedule
            })

        return data


class AllBroadcastTodayScheduleView(AllBroadcastDailyScheduleDAV, TodayArchiveView):
    """Today's all movie schedule from database in JSON."""

    model = MovieSchedule
    date_field = 'start_time'
    allow_future = True


class MovieScheduleCompanyDailyView(generics.ListAPIView):
    """API Endpoint to GET daily movie schedule for a broadcast company."""
    queryset = MovieSchedule.objects.all()      # Must set 'queryset' or override 'get_queryset()' method
    serializer_class = MovieScheduleSerializer

    def get(self, request, pk, year, month, day, format=None):
        """Get daily schedule for a broadcast company from database."""
        broadcast_company = get_object_or_404(BroadcastCompany, id=pk)

        queryset = MovieSchedule.objects.filter(Q(broadcast_company=broadcast_company) &
                                                Q(start_time__day=day, start_time__month=month, start_time__year=year))

        # 'many=True' option makes MovieScheduleSerializer return ListSerializer.
        serializer = MovieScheduleSerializer(queryset, many=True)
        return Response(serializer.data)
