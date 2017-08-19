web: bin/start-nginx bin/start-pgbouncer-stunnel gunicorn boomerang.wsgi -c config/gunicorn.py
release: python manage.py migrate
