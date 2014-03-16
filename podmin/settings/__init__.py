import os
import importlib

ENVIRONMENT = os.getenv("DJANGO_ENVIRONMENT")

importlib.import_module('podmin.settings.%s.*' % ENVIRONMENT)


try:
    from local import *
except ImportError:
    pass
