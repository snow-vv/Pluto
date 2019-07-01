# -*- coding: UTF-8 -*-

import os

APP_LOG_DIR = '/data/log/medivh/app'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'profile': {
            'format': '%(asctime)s %(message)s'
        }
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(APP_LOG_DIR, 'default.log'),
            'formatter': 'verbose',
        },
        'info_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(APP_LOG_DIR, 'info.log'),
            'formatter': 'verbose',
        },
        'error_handler': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(APP_LOG_DIR, 'error.log'),
            'formatter': 'verbose',
        },
        'profile_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(APP_LOG_DIR, 'profile.log'),
            'formatter': 'profile',
        },
        # 'sentry_handler': {
        #     'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.
        #     'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        # },
    },

    'loggers': {
        'django': {
            'handlers': ['default'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['error_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
        'info_logger': {
            'handlers': ['info_handler', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'error_logger': {
            'handlers': ['error_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
        'profile_logger': {
            'handlers': ['profile_handler'],
            'level': 'INFO',
            'propagate': False,
        },

    }
}
