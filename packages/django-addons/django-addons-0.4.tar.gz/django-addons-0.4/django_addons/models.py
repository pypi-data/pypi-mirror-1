# -*- coding: utf-8 -*-
from autodiscover import autodiscover

"""
Django Addons app automatically looks for handlers.py in addon folders,
loads the module and calls connect() on it to connect signal handlers.
Similar operation is performed on notifications.py to load
notification types for each addon.
"""

# DONT PUT THIS TO __init__.py!
autodiscover()
