web: bin/start-pgbouncer-stunnel gunicorn boomerang.wsgi --bind 0.0.0.0:$PORT --worker-class gevent --config boomerang/gunicorn_conf.py --log-file -
release: python manage.py migrate
