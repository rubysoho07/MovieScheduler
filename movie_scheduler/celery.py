from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_scheduler.settings')

app = Celery('movie_scheduler')

# Using a string here means the worker don't have to serialize
# the configuration object to child process.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a 'CELERY_' prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(BROKER_URL=os.environ['REDIS_URL'])

app.conf.beat_schedule = {
    # Get schedule from CJ E&M channels.
    'get_ocn_schedule': {
        'task': 'scheduler_core.tasks.save_cj_channel_schedule',
        'schedule': crontab(minute=30, hour=1),
        'args': ("OCN", "http://ocn.tving.com/ocn/schedule?startDate="),
    },
    'get_superaction_schedule': {
        'task': 'scheduler_core.tasks.save_cj_channel_schedule',
        'schedule': crontab(minute=31, hour=1),
        'args': ("SuperAction", "http://superaction.tving.com/superaction/schedule?startDate="),
    },
    'get_chcgv_schedule': {
        'task': 'scheduler_core.tasks.save_cj_channel_schedule',
        'schedule': crontab(minute=32, hour=1),
        'args': ("Ch.CGV", "http://chcgv.tving.com/chcgv/schedule?startDate="),
    },
    'get_catchon1_schedule': {
        'task': 'scheduler_core.tasks.save_cj_channel_schedule',
        'schedule': crontab(minute=33, hour=1),
        'args': ("CatchOn1", "http://catchon.tving.com/catchon/schedule1?startDate="),
    },
    'get_catchon2_schedule': {
        'task': 'scheduler_core.tasks.save_cj_channel_schedule',
        'schedule': crontab(minute=34, hour=1),
        'args': ("CatchOn2", "http://catchon.tving.com/catchon/schedule2?startDate="),
    },

    # Get schedule from t.cast channels.
    'get_screen_schedule': {
        'task': 'scheduler_core.tasks.save_tcast_channel_schedule',
        'schedule': crontab(minute=30, hour=4),
        'args': ("Screen", "http://www.imtcast.com/screen/program/schedule.jsp"),
    },
    'get_cinef_schedule': {
        'task': 'scheduler_core.tasks.save_tcast_channel_schedule',
        'schedule': crontab(minute=32, hour=4),
        'args': ("Cinef", "http://www.imtcast.com/cinef/program/schedule.jsp"),
    },

    # Modify schedule of CJ E&M channels.
    'modify_ocn_schedule': {
        'task': 'scheduler_core.tasks.get_modified_cj_schedule',
        'schedule': crontab(minute=0, hour=2),
        'args': ("OCN", "http://ocn.tving.com/ocn/schedule?startDate="),
    },
    'modify_chcgv_schedule': {
        'task': 'scheduler_core.tasks.get_modified_cj_schedule',
        'schedule': crontab(minute=0, hour=2),
        'args': ("Ch.CGV", "http://chcgv.tving.com/chcgv/schedule?startDate="),
    },
    'modify_superaction_schedule': {
        'task': 'scheduler_core.tasks.get_modified_cj_schedule',
        'schedule': crontab(minute=0, hour=2),
        'args': ("SuperAction", "http://superaction.tving.com/superaction/schedule?startDate="),
    },

    # Delete schedule of last week.
    'delete_last_week_schedule': {
        'task': 'scheduler_core.tasks.clear_last_week_schedule',
        'schedule': crontab(minute=0, hour=3, day_of_week='mon'),
        'args': (),
    },
}

# Set timezone for KST.
app.conf.timezone = 'Asia/Seoul'


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
