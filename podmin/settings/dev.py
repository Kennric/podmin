import os
from common import *

# Dev settings for PodMin
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

"""
The following rely on variables that should be set in the environment. The
Dev environment uses sqlite, so no db vars are needed.
Make sure you set:
    PODMIN_DEV_SECRET_KEY
    PODMIN_DEV_MEDIA_ROOT
    PODMIN_DEV_MEDIA_URL
    PODMIN_DEV_STATIC_ROOT
    PODMIN_DEV_BUFFER_ROOT
from somewhere before the settings are loaded.
"""

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.environ['PODMIN_DEV_MEDIA_ROOT']

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = os.environ['PODMIN_DEV_MEDIA_URL']

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.environ['PODMIN_DEV_STATIC_ROOT']

BUFFER_ROOT = os.environ['PODMIN_DEV_BUFFER_ROOT']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/podmin/db',
    }
}

SECRET_KEY = os.environ['PODMIN_DEV_SECRET_KEY']
