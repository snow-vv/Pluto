# -*- coding: UTF-8 -*-

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
import os

import raven

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 设置为mysql数据库
        'NAME': 'medivh',

        'USER': 'root',
        'PASSWORD': '',
        'HOST': '',
        'PORT': 3306,
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
            "charset": "utf8mb4",  # 为了支持emoji表情
        },
    },
}
CELERY_BROKER_URL = "redis://127.0.0.1:6379"
PRIVATE_KEY_FILE = 'xxxx/id_rsa.pub'
HIPCHAT_TOKEN = ''
HIPCHAT_HOST = 'https://hipchat.gengmei.cc/'
ALLOWED_HOSTS = ['ops.gengmei.cc???']

GM_CONFIG_PATH = ''  # ops/config 项目的路径
GM_CONFIG_REPO = 'git@git.wanmeizhensuo.com:ops/configs.git'

HIPCHAT_TASK_ROOM = 194   # 填写需要发送通知的hipchat room id
HIPCHAT_LOG_ROOM = 194     # 填写需要发送通知的hipchat room id
HIPCHAT_PLAN_STATUS_ROOM = 194  # 填写需要发送通知的hipchat room id

SENTRY_CELERY_ENDPOINT = ''    # celery sentry
RAVEN_CONFIG = {
    'dsn': '',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(BASE_DIR),
}   # django sentry
