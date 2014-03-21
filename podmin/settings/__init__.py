import os
import importlib

ENVIRONMENT = os.getenv("DJANGO_ENVIRONMENT")

print ENVIRONMENT

# why won't this work? .* doesn't, either
#env_settings = importlib.import_module('podmin.settings.%s' % ENVIRONMENT)

if ENVIRONMENT == 'dev':
    print "dev detected!"
    from dev import *

if ENVIRONMENT == 'staging':
    print "staging detected!"
    from staging import *

if ENVIRONMENT == 'production':
    print "production detected!"
    from production import *
