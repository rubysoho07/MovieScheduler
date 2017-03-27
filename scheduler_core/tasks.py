from __future__ import absolute_import, unicode_literals

from django.utils import timezone

from celery import shared_task

from scheduler_core.movie_schedule_parser import MovieScheduleParser
from scheduler_core.models import BroadcastCompany, LatestUpdate


# Create your tasks here.
@shared_task(max_retries=2, default_retry_delay=60 * 60)
def save_cj_channel_schedule(channel_name, url_pattern):
    """ Save CJ E&M Channels' schedule. """
    # If channel_name is None, add to database of channels.
    channel, _ = BroadcastCompany.objects.get_or_create(bc_name=channel_name)

    # If last_date doesn't exist, add today's date to database of last_date.
    last_date, created = LatestUpdate.objects.get_or_create(broadcast_company=channel)
    if created is True:
        last_date.latest_update = timezone.now()
        last_date.save()

    # Get schedule with movie_schedule_parser
    date_str = timezone.datetime.strftime(last_date.latest_update, "%Y%m%d")
    schedules = MovieScheduleParser.get_cj_channels(url_pattern + date_str)
    while schedules is not None:
        # Add schedules
        MovieScheduleParser.save_schedule(channel, schedules)

        # Save last_date and go to the next day.
        last_date.latest_update = last_date.latest_update + timezone.timedelta(days=1)
        last_date.save()
        print ("[" + channel_name + "] Next Date : " + str(last_date.latest_update))
        date_str = timezone.datetime.strftime(last_date.latest_update, "%Y%m%d")
        schedules = MovieScheduleParser.get_cj_channels(url_pattern + date_str)


@shared_task(max_retries=2, default_retry_delay=60 * 60)
def save_kakao_tv_schedule():
    """ Get Kakao TV Movie/Animation Channel Schedule. """
    # Get movie and animation schedule.
    movie_schedule, animation_schedule = MovieScheduleParser.get_kakao_tv_schedule()

    # Get or create broadcasting company information.
    movie_channel, _ = BroadcastCompany.objects.get_or_create(bc_name="PLAYY Movie")
    animation_channel, _ = BroadcastCompany.objects.get_or_create(bc_name="PLAYY Animation")

    # Save schedules
    if movie_channel is not None:
        MovieScheduleParser.save_schedule(movie_channel, movie_schedule)

    if animation_channel is not None:
        MovieScheduleParser.save_schedule(animation_channel, animation_schedule)

    # Update last update date.
    movie_channel_last_update, _ = LatestUpdate.objects.get_or_create(broadcast_company=movie_channel)
    movie_channel_last_update.latest_update = timezone.now()
    movie_channel_last_update.save()

    animation_channel_last_update, _ = LatestUpdate.objects.get_or_create(broadcast_company=animation_channel)
    animation_channel_last_update.latest_update = timezone.now()
    animation_channel_last_update.save()


@shared_task(max_retries=2, default_retry_delay=60*60)
def save_tcast_channel_schedule(channel_name, url):
    """ Get t.cast channel schedule(Screen, Cinef). """
    # If channel_name is None, add to database of channels.
    channel, _ = BroadcastCompany.objects.get_or_create(bc_name=channel_name)

    # If last_date doesn't exist, add today's date to database of last_date.
    last_date, created = LatestUpdate.objects.get_or_create(broadcast_company=channel)
    if created is True:
        last_date.latest_update = timezone.datetime.today()
        last_date.save()

    # Get schedule with movie_schedule_parser
    last_update_date = MovieScheduleParser.get_tcast_channel_schedules(channel, url, last_date.latest_update)

    # Update last update date.
    if last_update_date is not None:
        last_date.latest_update = last_update_date
        last_date.save()
