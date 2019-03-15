# cmd1="python manage.py runserver"
cmd1="python manage.py runserver_plus"
cmd1name="Django"
cmd2="redis-server"
cmd2name="Redis"
cmd3="celery -A project worker -l info -B --scheduler django_celery_beat.schedulers:DatabaseScheduler"
cmd3name="Celery"

trap 'kill %1; kill %2' SIGINT
$(eval $cmd1) | sed -e 's/^/[$cmd1name] /' & $(eval $cmd2) | sed -e 's/^/[cmd2name] /' & $(eval $cmd3) | sed -e 's/^/[cmd3name] /'
