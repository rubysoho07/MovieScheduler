from __future__ import absolute_import, unicode_literals

from django.utils import timezone
from django.db.models import Q

from celery import shared_task

from scheduler_core.movie_schedule_parser import MovieScheduleParser
from scheduler_core.models import BroadcastCompany, MovieSchedule, LatestUpdate


# Create your tasks here.
# Save CJ E&M Channels' schedule.
@shared_task(max_retries=2, default_retry_delay=60 * 60)
def save_cj_channel_schedule(channel_name, url_pattern):
    # If channel_name is None, add to database of channels.
    channel, created = BroadcastCompany.objects.get_or_create(bc_name=channel_name)

    # If last_date doesn't exist, add today's date to database of last_date.
    try:
        last_date = LatestUpdate.objects.filter(Q(broadcast_company=channel))[0]
    except IndexError:
        last_date = LatestUpdate(broadcast_company=channel, latest_update=timezone.now())
        last_date.save()

    # Get schedule with movie_schedule_parser
    date_str = timezone.datetime.strftime(last_date.latest_update, "%Y%m%d")
    schedules = MovieScheduleParser.get_cj_channels(url_pattern + date_str)
    while schedules is not None:

        # Add schedules
        for item in schedules:
            new_schedule = MovieSchedule(broadcast_company=channel,
                                         title=item['title'],
                                         start_time=item['start_time'],
                                         end_time=item['end_time'],
                                         ratings=MovieScheduleParser.get_cj_channel_ratings(item['rating']))
            new_schedule.save()

        # Save last_date and go to the next day.
        last_date.latest_update = last_date.latest_update + timezone.timedelta(days=1)
        last_date.save()
        print ("[" + channel_name + "] Next Date : " + str(last_date.latest_update))
        date_str = timezone.datetime.strftime(last_date.latest_update, "%Y%m%d")
        schedules = MovieScheduleParser.get_cj_channels(url_pattern + date_str)


# Get Kakao TV Movie/Animation Channel Schedule.
@shared_task(max_retries=2, default_retry_delay=60 * 60)
def save_kakao_tv_schedule():

    # Get movie and animation schedule.
    movie_schedule, animation_schedule = MovieScheduleParser.get_kakao_tv_schedule()

    # Get or create broadcasting company information.
    movie_channel, _ = BroadcastCompany.objects.get_or_create(bc_name="PLAYY Movie")
    animation_channel, _ = BroadcastCompany.objects.get_or_create(bc_name="PLAYY Animation")

    # Save schedules
    if len(movie_channel) != 0:
        MovieScheduleParser.save_kakao_schedule(movie_channel, movie_schedule)

    if len(animation_channel) != 0:
        MovieScheduleParser.save_kakao_schedule(animation_channel, animation_schedule)

    # Update last update date.
    movie_channel_last_update, _ = LatestUpdate.objects.get_or_create(broadcast_company=movie_channel)
    movie_channel_last_update.latest_update = timezone.now()
    movie_channel_last_update.save()

    animation_channel_last_update, _ = LatestUpdate.objects.get_or_create(broadcast_company=animation_channel)
    animation_channel_last_update.latest_update = timezone.now()
    animation_channel_last_update.save()
