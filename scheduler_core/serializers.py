from scheduler_core.models import MovieSchedule, BroadcastCompany
from rest_framework import serializers


class MovieScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Movie Schedule."""
    class Meta:
        model = MovieSchedule
        fields = ('title', 'start_time', 'ratings')


class BroadcastCompanySerializer(serializers.ModelSerializer):
    """Serializer for Broadcast company."""
    class Meta:
        model = BroadcastCompany
        fields = ('id', 'bc_name')
