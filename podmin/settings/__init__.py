import os
import importlib

ENVIRONMENT = os.getenv("DJANGO_ENVIRONMENT")

# why won't this work? .* doesn't, either
#env_settings = importlib.import_module('podmin.settings.%s' % ENVIRONMENT)

if ENVIRONMENT == 'dev':
    from dev import *

if ENVIRONMENT == 'staging':
    from staging import *

if ENVIRONMENT == 'production':
    from production import *
