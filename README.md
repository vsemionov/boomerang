Boomerang
=========

An experimental web application
-------------------------------

[![Build Status](https://travis-ci.org/vsemionov/boomerang.svg?branch=master)](https://travis-ci.org/vsemionov/boomerang)


### Features
* Support for offline data synchronization with conflict detection
* Fuzzy (approximate) full-text search
* Social login with automatic verified account linking
* Request rate throttling and resource quotas
* REST API


### Website

https://boomerang-core.herokuapp.com/


### Deployment

#### Pre-install
* create facebook and google social applications
* update the target domain and server email in *boomerang/settings.py*
* commit changes: `git commit -a -m "configured"`

#### Local
* install *python* (3.6)
* setup *postgresql* (it is possible to use a different database, but fuzzy search will not work)
* setup *redis* (it is possible to deploy without redis with a different cache configuration in the settings)
* update *settings.py* to point to the configured services
* (optional) update *settings.py* with the allowed origins and redirect urls
* install python packages: `pip install -r requirements.txt` (preferably in a virtualenv)
* create the database: `sudo -u postgres createuser -P boomerang && sudo -u postgres createdb -O boomerang boomerang && sudo -u postgres psql -c "create extension pg_trgm;" boomerang`
* initialize the database: `./manage.py migrate`
* create the superuser: `./manage.py createsuperuser`
* start the server: `./manage.py runserver`
* perform routine maintenance: `bin/maintenance.sh`

#### Heroku
* install *heroku toolbelt*
* create a heroku application; add buildpacks *heroku/python*, *https://github.com/heroku/heroku-buildpack-pgbouncer*, and *https://github.com/agriffis/nginx-buildpack*; provision *heroku postgres*, *heroku redis*, and *heroku scheduler*
* (optional) create a *sentry* project or provision *sentry* from heroku
* connect: `heroku login && heroku git:remote -a <app_name>`
* configure: `heroku config:set SECRET_KEY=<secret_key> ALLOW_ORIGIN=<optional_origin> FRONTEND_LOGIN_REDIRECT_URL=<optional_url> EMAIL_PASSWORD=<email_password> SENTRY_DSN=<sentry_dsn>` (set `SENTRY_DSN` only if a sentry project was created manually)
* example production configuration
    * ALLOW_ORIGIN
    * DATABASE_URL
    * EMAIL_PASSWORD
    * FRONTEND_LOGIN_REDIRECT_URL
    * NUM_WORKERS
    * PGBOUNCER_DEFAULT_POOL_SIZE
    * PGBOUNCER_MIN_POOL_SIZE
    * PGBOUNCER_RESERVE_POOL_SIZE
    * REDIS_MAX_CONNS
    * REDIS_URL
    * SECRET_KEY
    * SENTRY_DSN
* deploy: `git push heroku`
* create superuser: `heroku run python manage.py createsuperuser`
* schedule daily maintenance: `bin/maintenance.sh`


#### Post-install
* login to */admin/*, edit the site and create the social applications
