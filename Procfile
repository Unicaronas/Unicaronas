web: gunicorn project.wsgi --log-file -
worker: celery -A project worker -l info -B --scheduler django_celery_beat.schedulers:DatabaseScheduler
release: python manage.py migrate
