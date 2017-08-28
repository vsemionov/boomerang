Boomerang
=========

An experimental web application
-------------------------------

[![Build Status](https://travis-ci.org/vsemionov/boomerang.svg?branch=master)](https://travis-ci.org/vsemionov/boomerang)


### Features
* Support for data synchronization with conflict detection
* Fuzzy (approximate) full-text search
* Social login with automatic verified account linking
* Request rate throttling and resource quotas
* REST API


### Website

https://boomerang-core.herokuapp.com/


### Data Synchronization

The API is designed to support data synchronization by offline clients, such as mobile applications. This is accomplished by the following approach:
* Aggregate list endpoints per object type are exposed. This allows all objects of a given type to be retrieved in a single request, even if they are nested into different objects. For example, in the hierarchy notebook/note, there is a note list endpoint that returns all notes from all notebooks.
  - The choice to expose one endpoint per object type, as opposed to a single endpoint for all synchronized types, was made because the latter approach produces a response that is an object (as opposed to a list). This does not allow paginating responses and forces the use of a single request. Avoiding multiple round-trip times is still possible by pipelining requests for different object types.
* List endpoints allow the client to specify the minimum modification time of the returned objects. The returned data contains the request execution timestamp. To synchronize incrementally, the client must store this timestamp and send it as the minimum modification time during their next synchronization.
  - Since the synchronization is performed across multiple requests, their results may be inconsistent if objects are modified between the requests. To counter this, the endpoints also accept the maximum modification timestamp of the returned objects as a parameter. All requests after the first one in a single synchronization session should set this parameter to the request execution timestamp from the first response.
* Deletion of objects is performed softly. Upon deletion, a hidden flag is toggled, but the data itself is not removed. This allows offline clients to detect which locally-existing objects have been deleted on the server.
  - However, to preserve system resources, objects that are deleted a specified time ago are periodically removed. Also, the number of deleted objects is limited. When an object is being deleted and this limit is reached, the object with the oldest deletion timestamp is removed.
* Deleted objects are listed in separate (aggregate) endpoints, which also accept a minimum deletion timestamp parameter.
  - The server is able to detect if the generated listing is complete for the requested minimum modification timestamp. If objects may have removed due to expiry or an exceeded limit, a different response status code is returned. In this case, the client must retrieve the full list of non-deleted objects and determine the deleted ones by comparing to their local database.

#### Conflict Detection

The API also supports conflict detection when a write request is made from a client for an object, whose contents on the client are older than the contents on the server. This is beneficial for offline as well as online clients. The approach is the following:
* Endpoints that modify the state of an object accept a last modification timestamp. Clients shall set it to the object's modification timestamp in their database. If it does not match the object's modification timestamp on the server, the request is rejected.
* When a conflict occurs, it is up to the client to decide how to handle it. Some possibilities are:
  - Synchronize the newer object state on both sides.
  - Create a copy of the object.
  - Duplicate the two versions on both sides.


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
