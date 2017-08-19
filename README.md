Boomerang
=========

An experimental web application
-------------------------------


### Features
* Support for data synchronization with conflict detection
* Fuzzy (approximate) full-text search
* Social login with automatic verified account linking
* Request rate throttling and resource quotas
* REST API


### Location

https://boomerang-core.herokuapp.com/


### Deployment

#### Pre-install
* create facebook and google social applications
* update the target domain and server email in *boomerang/settings.py*
* commit changes: `git commit -a -m "configured"`

#### Local
* install *python* (3.6)
* setup services: *postgresql* and *redis*
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
* create a heroku application; add buildpacks *heroku/python*, *https://github.com/heroku/heroku-buildpack-pgbouncer*, and *https://github.com/vsemionov/nginx-buildpack*; provision *heroku postgres*, *heroku redis*, and *heroku scheduler*
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


### Roadmap

* 0.1
    - database model
    - REST API
    - hosting

* 0.2
    - social login
    - user registration
    - email authentication

* 0.3
    - API rate/size/count limits

* 0.4
    - data synchronization API support

* 0.5
    - search API support

* 0.6
    - cross-origin front-end support
    - monitoring
