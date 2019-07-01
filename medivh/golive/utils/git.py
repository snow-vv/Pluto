# -*- coding: UTF-8 -*-
from django.conf import settings
from git.cmd import Git

gm_ops_config_git = Git(settings.GM_CONFIG_PATH)
