#!/usr/bin/env python

from sys import argv

# Log to syslog
import logging, logging.handlers

logger = logging.root
str_fmt = '%(asctime)s ' + argv[0] + ': ' + logging.BASIC_FORMAT
date_fmt = '%b %d %H:%M:%S'
log_fmt = logging.Formatter(str_fmt, date_fmt)
h1 = logging.handlers.SysLogHandler(address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_LOCAL0)
h2 = logging.StreamHandler()
h1.setFormatter(log_fmt)
h2.setFormatter(log_fmt)
logger.addHandler(h1)
logger.addHandler(h2)

# Django Preamble
import sys, os.path
sys.path.append(os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
if settings.RUNSCRIPT_DEBUG:
        logger.setLevel(logging.DEBUG)
else:
        logger.setLevel(logging.INFO)

mod = __import__(argv[1], fromlist=[argv[2]])
func = getattr(mod, argv[2])
func(*argv[3:])
