# -*- coding: utf-8 -*-

from .base import *

INSTALLED_APPS += ('django_extensions',)

INSTALLED_APPS += ('django_nose',)
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    '--cover-html',
    '--cover-package=api'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'migration': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'django.db': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

CONSTANCE_CONFIG = {
    'CTF_START_AT': (datetime.datetime.now(), 'Date to start CTF'),
    'CTF_END_AT': (datetime.datetime.now() + datetime.timedelta(days=365), 'Date to end CTF'),
}
