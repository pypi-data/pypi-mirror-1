# -*- coding: utf-8 -*-

"""
Django Addons app automatically looks for handlers.py in addon folders,
loads the module and calls connect() on it to connect signal handlers.
Similar operation is performed on notifications.py to load
notification types for each addon.
"""

import os
import sys
from django.conf import settings
from django.conf.urls.defaults import *

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

def autodiscover_handlers():
    """
    Register signal handlers from each addon.
    """
    for addon in settings.ADDONS:
        fullname = "%s.%s.handlers" % (settings.ADDONS_PREFIX, addon)
        try:
            __import__(fullname)
        except ImportError:
            pass
        if fullname in sys.modules:
            handlers = sys.modules[fullname]
            handlers.connect()

def autodiscover_notifications():
    """
    Register notifications from each addon.
    TODO: Implement this with signals. Requires changes in django-notifications upstream.
    """
    for addon in settings.ADDONS:
        fullname = "%s.%s.notifications" % (settings.ADDONS_PREFIX, addon)
        try:
            __import__(fullname)
        except ImportError:
            pass

ADDONS_LOADED = False
def autodiscover():
    """
    This should be called from main urls.py like this: 
    import django_addons
    django_addons.autodiscover()
    """
    global ADDONS_LOADED
    if ADDONS_LOADED:
        return
    ADDONS_LOADED = True

    autodiscover_notifications()
    autodiscover_handlers()


