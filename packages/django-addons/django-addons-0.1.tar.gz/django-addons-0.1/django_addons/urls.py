# -*- coding: utf-8 -*-

"""
This is django_addons.urls module, it loads URLconf of
each addon.

In main urls you should have something like:

  urlpatterns += patterns('', (r'', include('django_addons.urls')))

"""

import os
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('')

for addon in settings.ADDONS:
    filename = "%s/%s/urls.py" % (settings.ADDONS_ROOT, addon)
    fullname = "%s.%s.urls" % (settings.ADDONS_PREFIX, addon)
    if os.path.exists(filename):
        urlpatterns += patterns('',
            url(r'', include(fullname)),
        )
