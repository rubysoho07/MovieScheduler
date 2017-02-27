from django.views.generic.list import ListView

from scheduler_core.models import MovieSchedule


# Create your views here.
class MovieScheduleListView(ListView):
    model = MovieSchedule
