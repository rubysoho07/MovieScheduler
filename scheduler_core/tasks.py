from __future__ import absolute_import, unicode_literals

from django.utils import timezone

from celery import shared_task

from scheduler_core.movie_schedule_parser import CJScheduleParser, TCastScheduleParser
from scheduler_core.models import BroadcastCompany, LatestUpdate


# Create your tasks here.
@shared_task(max_retries=2, default_retry_delay=60 * 60)
def save_cj_channel_schedule(channel_name, url_pattern):
    """Save CJ E&M Channels' schedule."""
    parser = CJScheduleParser()

    channel, _ = BroadcastCompany.objects.get_or_create(bc_name=channel_name)

    last_date, created = LatestUpdate.objects.get_or_create(broadcast_company=channel)
    if created is True:
        last_date.latest_update = timezone.now()
        last_date.save()

    # Get schedule
    date_str = timezone.datetime.strftime(last_date.latest_update, "%Y%m%d")
    schedules = parser.get_channel_schedule(url_pattern + date_str)
    while schedules is not None:
        parser.save_schedule(channel, schedules)

        # Save latest update date and go to the next day.
        last_date.latest_update = last_date.latest_update + timezone.timedelta(days=1)
        last_date.save()
        print("[" + channel_name + "] Next Date : " + str(last_date.latest_update))
        date_str = timezone.datetime.strftime(last_date.latest_update, "%Y%m%d")
        schedules = parser.get_channel_schedule(url_pattern + date_str)


@shared_task(max_retries=2, default_retry_delay=60*60)
def save_tcast_channel_schedule(channel_name, url):
    """Get t.cast channel schedule."""

    channel, _ = BroadcastCompany.objects.get_or_create(bc_name=channel_name)

    last_date, created = LatestUpdate.objects.get_or_create(broadcast_company=channel)
    if created is True:
        last_date.latest_update = timezone.datetime.today()
        last_date.save()

    parser = TCastScheduleParser(channel, last_date.latest_update)
    latest_update_date = parser.get_channel_schedule(url)

    # Update last update date.
    if latest_update_date is not None:
        last_date.latest_update = latest_update_date
        last_date.save()
