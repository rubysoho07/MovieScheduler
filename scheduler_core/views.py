from django.views.generic.base import TemplateView
from django.views.generic.dates import DayArchiveView, TodayArchiveView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404

from django.db.models import Q

from scheduler_core.models import MovieSchedule, BroadcastCompany

from rest_framework import generics
from rest_framework.response import Response
from scheduler_core.serializers import MovieScheduleSerializer, BroadcastCompanySerializer


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


class BroadcastCompanyView(generics.ListAPIView):
    """API Endpoint to GET information of broadcast companies."""

    queryset = BroadcastCompany.objects.all()
    serializer_class = BroadcastCompanySerializer

    def get(self, request, *args, **kwargs):
        queryset = BroadcastCompany.objects.all()
        # 'many=True' option makes BroadcastCompanySerializer return ListSerializer.
        serializer = BroadcastCompanySerializer(queryset, many=True)
        return Response(serializer.data)
