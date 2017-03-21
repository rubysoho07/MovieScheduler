from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_scheduler.settings')

# Include scheduler_core.tasks to import
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
    # Executes every day at 0:30.
    'get_ocn_schedule': {
        'task': 'scheduler_core.tasks.save_cj_channel_schedule',
        'schedule': crontab(minute=30, hour=0),
        'args': ("OCN", "http://ocn.tving.com/ocn/schedule?startDate="),
    },
    'get_superaction_schedule': {
        'task': 'scheduler_core.tasks.save_cj_channel_schedule',
        'schedule': crontab(minute=30, hour=0),
        'args': ("SuperAction", "http://superaction.tving.com/superaction/schedule?startDate="),
    },
    'get_chcgv_schedule': {
        'task': 'scheduler_core.tasks.save_cj_channel_schedule',
        'schedule': crontab(minute=30, hour=0),
        'args': ("Ch.CGV", "http://chcgv.tving.com/chcgv/schedule?startDate="),
    },
    'get_catchon1_schedule': {
        'task': 'scheduler_core.tasks.save_cj_channel_schedule',
        'schedule': crontab(minute=30, hour=0),
        'args': ("CatchOn1", "http://catchon.tving.com/catchon/schedule1?startDate="),
    },
    'get_catchon2_schedule': {
        'task': 'scheduler_core.tasks.save_cj_channel_schedule',
        'schedule': crontab(minute=30, hour=0),
        'args': ("CatchOn2", "http://catchon.tving.com/catchon/schedule2?startDate="),
    },
    # Execute 06:30 on every Saturday.
    'get_kakao_tv_schedule': {
        'task': 'scheduler_core.tasks.save_kakao_tv_schedule',
        'schedule': crontab(minute=30, hour=6, day_of_week='sat'),
        'args': (),
    },
}

# Set timezone for KST.
app.conf.timezone = 'Asia/Seoul'


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
