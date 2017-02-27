web: gunicorn movie_scheduler.wsgi --log-file -
worker: celery -A movie_scheduler worker --loglevel=DEBUG -B --concurrency=1