# -*- coding: utf-8 -*-
import os
from .base import *

# FIXME: Dockerテスト用設定. 本番デプロイ時の構成に合わせて変更
ALLOWED_HOSTS = os.getenv('FLAGGER_ALLOWED_HOSTS_CSV').split(',')

DEBUG = False

STATIC_ROOT = '/var/www/static/'

# MIDDLEWARE += [
#     'common.middlewares.InternalAPICallMiddleware'
# ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('FLAGGER_MYSQL_DATABASE'),
        'USER': os.getenv('FLAGGER_MYSQL_USERNAME'),
        'PASSWORD': os.getenv('FLAGGER_MYSQL_PASSWORD'),
        'HOST': os.getenv('FLAGGER_MYSQL_HOSTNAME'),
        'PORT': '',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': 'TRADITIONAL,NO_AUTO_VALUE_ON_ZERO,ONLY_FULL_GROUP_BY',
        },
    },
}

MIDDLEWARE += [
    'scoreserver.middlewares.IPTrackingMiddleware',
    'scoreserver.middlewares.BlockBannedUserMiddleware'
]

SECRET_KEY = os.getenv("FLAGGER_DJANGO_SECRET_KEY")
JWT_AUTH = {
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=300),

    'JWT_ALLOW_REFRESH': False,

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,

}

CONSTANCE_CONFIG = {
    'CTF_START_AT': (datetime.datetime.now() + datetime.timedelta(days=14), 'Date to start CTF'),
    'CTF_END_AT': (datetime.datetime.now() + datetime.timedelta(days=27), 'Date to end CTF'),
}
