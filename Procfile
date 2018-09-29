web: gunicorn project.wsgi --log-file -
worker: celery -A project worker -l info
release: python manage.py migrate
