from __future__ import absolute_import, unicode_literals

import traceback

from django.core.mail import EmailMessage

from django.conf import settings

from django.template.loader import get_template

from django.utils import timezone

from django.db.models import Q

from celery import shared_task

from scheduler_core.movie_schedule_parser import CJScheduleParser, TCastScheduleParser
from scheduler_core.models import BroadcastCompany, LatestUpdate, MovieSchedule


# Create your tasks here.
def send_error_report(url, exception, trace):
    """Send email when an error occurs."""
    if settings.DEBUG is False:
        email_context = {
            'site': url,
            'exception': exception,
            'traceback': trace
        }
        message = get_template('scheduler_core/error_report_parsing.html').render(email_context)
        error_email = EmailMessage('[MovieScheduler] Parsing Error Report',
                                   message,
                                   settings.SERVER_EMAIL,
                                   settings.ADMINS)
        error_email.content_subtype = 'html'
        error_email.send(fail_silently=False)


@shared_task(max_retries=2, default_retry_delay=60 * 60)
def save_cj_channel_schedule(channel_name, url_pattern):
    """Save CJ E&M Channels' schedule."""
    parser = CJScheduleParser()
    date_str = None

    try:
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
    except Exception as e:
        send_error_report(url_pattern+date_str, e, traceback.format_exc())


@shared_task(max_retries=2, default_retry_delay=60*60)
def save_tcast_channel_schedule(channel_name, url):
    """Get t.cast channel schedule."""
    try:
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

        print("[" + channel_name + "] Last update date : " + str(last_date.latest_update))
    except Exception as e:
        send_error_report(url, e, traceback.format_exc())


@shared_task(max_retries=2, default_retry_delay=60*60)
def clear_last_week_schedule():
    """Delete all schedules before 1 week."""
    try:
        today_date = timezone.datetime.today() - timezone.timedelta(days=1)
        MovieSchedule.objects.filter(start_time__lt=today_date).delete()
    except Exception as e:
        send_error_report(None, e, traceback.format_exc())


@shared_task()
def get_modified_cj_schedule(channel_name, url_pattern):
    """Modify today's schedule of CJ E&M channels."""
    parser = CJScheduleParser()
    date_str = None

    try:
        channel = BroadcastCompany.objects.get(bc_name=channel_name)

        date_str = timezone.datetime.strftime(timezone.datetime.today(), "%Y%m%d")
        schedules = parser.get_channel_schedule(url_pattern + date_str)

        if schedules is not None:
            start_time = schedules[0]['start_time'] - timezone.timedelta(minutes=30)
            end_time = schedules[len(schedules)-1]['start_time'] + timezone.timedelta(minutes=30)

            # Remove old schedule. (from start_time to end_time)
            old_schedules = MovieSchedule.objects.filter(Q(start_time__range=(start_time, end_time)) &
                                                         Q(broadcast_company=channel))
            old_schedules.delete()

            # Save schedule.
            parser.save_schedule(channel, schedules)
            print("[" + channel_name + "] Schedule has changed.")
        else:
            print("[" + channel_name + "] No changes detected.")
    except Exception as e:
        send_error_report(url_pattern+date_str, e, traceback.format_exc())
