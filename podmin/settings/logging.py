import os

LOGFILE = os.getenv('PODMIN_LOGFILE', 'logs/podmin.log')
LOG_LEVEL = os.getenv('PODMIN_LOG_LEVEL', 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'  # noqa
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'filters': ['require_debug_true'],
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'filters': ['require_debug_false'],
            'level': 'CRITICAL',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'logfile': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGFILE,
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null', 'logfile'],
            'propagate': True,
            'level': LOG_LEVEL,
        },
        'django.request': {
            'handlers': ['mail_admins', 'logfile'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'podmin': {
            'handlers': ['logfile'],
            'level': LOG_LEVEL,
            'propagate': True,
        }
    }
}
