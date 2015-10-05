import os.path
from image_settings import *
from logging import *

# Django settings for podcaster project.

PROJECT_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))

# FIXTURE_DIRS = (os.path.join(
#    os.path.basename(__file__), '../', 'fixtures/'))

SITE_ROOT = os.path.normpath(os.path.join(PROJECT_ROOT, '../'))

TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
LOGIN_URL = '/login'
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'podmin.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # '/home/kennric/projects/podcaster/templates',
    # os.path.join(os.path.basename(__file__), 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'form_utils',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'podmin'
)


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
The following can use variables set in the environment.
To use the environment for settings, be sure you set:
    PODMIN_DB_ENGINE
    PODMIN_DB_NAME
    PODMIN_DB_USER
    PODMIN_DB_PASS
    PODMIN_DB_HOST
    PODMIN_DB_PORT
    PODMIN_SECRET_KEY
    PODMIN_MEDIA_ROOT
    PODMIN_MEDIA_URL
    PODMIN_STATIC_ROOT
    PODMIN_BUFFER_ROOT
    PODMIN_STATIC_URL
    PODMIN_DEBUG
    PODMIN_TEMPLATE_DEBUG

in the wsgi environment before the settings are loaded.
"""

DEBUG = os.getenv('PODMIN_DEBUG', False)
TEMPLATE_DEBUG = os.getenv('PODMIN_DEBUG', False)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.getenv('PODMIN_MEDIA_ROOT',
                       os.path.normpath(os.path.join(SITE_ROOT, '/media/')))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = os.getenv('PODMIN_MEDIA_URL', '/media/')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

STATIC_ROOT = os.getenv('PODMIN_STATIC_ROOT',
                        os.path.normpath(os.path.join(SITE_ROOT, '/static/')))

STATIC_URL = os.getenv('PODMIN_STATIC_URL', '/static/')

BUFFER_ROOT = os.getenv('PODMIN_BUFFER_ROOT', '/buffer/')

SECRET_KEY = os.getenv('PODMIN_SECRET_KEY', '8d2c94e759dc865d5234e0e70e0f5530')

DATABASES = {
    'default': {
        'ENGINE': os.getenv('PODMIN_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('PODMIN_DB_NAME', 'db/podmin.db'),
        'USER': os.getenv('PODMIN_DB_USER', ''),
        'PASSWORD': os.getenv('PODMIN_DB_PASS', ''),
        'HOST': os.getenv('PODMIN_DB_HOST', ''),
        'PORT': os.getenv('PODMIN_DB_PORT', '')
    }
}


