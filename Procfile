web: newrelic-admin run-program gunicorn movie_scheduler.wsgi --log-file -
worker: celery -A movie_scheduler worker --loglevel=INFO -B --concurrency=1