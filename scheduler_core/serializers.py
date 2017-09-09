from scheduler_core.models import MovieSchedule
from rest_framework import serializers


class MovieScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Movie Schedule."""
    class Meta:
        model = MovieSchedule
        fields = ('title', 'start_time', 'ratings')
