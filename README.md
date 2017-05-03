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


### Deployment

#### Pre-install
* update *boomerang/settings.py* with the target domain and server email
* commit changes: `git commit -a -m "configured"`

#### Local
* install *python* (3.6)
* install *node.js* (and *npm*)
* install *heroku* toolbelt
* setup services: *postgresql* and *redis*
* update *settings.py* to point to the configured services
* install python packages: `pip install -r requirements.txt`
* create the database: `sudo -u postgres createuser -P boomerang && sudo -u postgres createdb -O boomerang boomerang && sudo -u postgres psql -c "create extension pg_trgm;" boomerang`
* initialize the database: `./manage.py migrate`
* create the superuser: `./manage.py createsuperuser`
* build the front-end: `npm install`
* start the server: `./manage.py runserver`
* perform routine maintenance: `bin/maintenance.sh`

#### Heroku
* create a heroku python application, insert buildpack *heroku/nodejs* before *heroku/python*, provision *heroku postgres*, *heroku redis*, and *heroku scheduler*
* connect: `heroku login && heroku git:remote -a <app_name>`
* configure: `heroku config:set EMAIL_PASSWORD=<email_password>`
* deploy: `git push heroku`
* create superuser: `heroku run python manage.py createsuperuser`
* schedule daily maintenance: `bin/maintenance.sh`

#### Post-install
* login to */admin/*, edit the site and create the social applications


### Roadmap

* 0.1
    + database model
    + REST API
    + hosting

* 0.2
    + social login
    + user registration
    + email authentication

* 0.3
    + API rate/size/count limits

* 0.4
    + data synchronization API support

* 0.5
    + search API support

* 0.6
    + web front end

* 0.7
    + note/task search in web app

* 0.8
    + android app

* 0.9
    + note/task search in mobile app

* 1.0
    + android app offline mode
    + android app data synchronization
