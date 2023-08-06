# -*- coding: utf-8 -*-

import os
import sys

from django.conf import settings
from django.conf.urls.defaults import *

VERSION = (0, 4, 0, 'final')

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3] != 'final':
        version = '%s %s' % (version, VERSION[3])
    return version

def dependency_found(addon):
    return addon in ( \
        getattr(settings, "ADDONS", []) + 
        getattr(settings, "ADDONS_PROVIDED", []))

def get_meta(addon):
    # Load metainformation
    name = "%s.%s" % (settings.ADDONS_PREFIX, addon)
    try:
        mod = None
        __import__(name)
        mod = sys.modules[name]
    except Exception, e:
        print e
        pass
    finally:
        return getattr(mod, 'Meta', None)



