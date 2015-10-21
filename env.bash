#!/bin/bash

# This is a convenience file to set podmin's env variables
# in the current shell for things like manage.py commands
# and running the dev server. Replace ENV with a supported
# environment, DEV, STG, PROD, and set DJANGO_ENVIRONMENT
# to the corresponding string, dev, staging, production.
export PYTHONPATH=/home/kennric/projects/podmin/
export DJANGO_ENVIRONMENT=env
export DJANGO_SETTINGS_MODULE=podmin.settings
export PODMIN_DEV_STATIC_ROOT=/tmp/podmin/static
export PODMIN_DEV_MEDIA_ROOT=/tmp/podmin/media
export PODMIN_DEV_MEDIA_URL=http://example.com/media/
export PODMIN_DEV_BUFFER_ROOT=/tmp/p/
export PODMIN_DEV_DB_ENGINE=django.db.backends.mysql
export PODMIN_DEV_DB_NAME=podmin
export PODMIN_DEV_DB_USER=podmin
export PODMIN_DEV_DB_PASS=secret
export PODMIN_DEV_DB_HOST=127.0.0.1
export PODMIN_DEV_DB_PORT=3306
export PODMIN_DEV_SECRET_KEY="8kf-rst4iw64xiie(^fze2ps-t7%#s1*e&fm+@io&(&*c5ot0a"
