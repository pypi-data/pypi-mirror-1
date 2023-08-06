# -*- coding: utf-8 -*-

from django.conf import settings
#from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response #, get_object_or_404
from django.template import RequestContext

from django_addons import get_meta

def addons_view(request):
    
    addons = {}
    for addon in settings.ADDONS:
        addons[addon] = dict()
        addons[addon]["meta"] = get_meta(addon)
        addons[addon]["enabled"] = True
        

    for addon in settings.ADDONS_DISABLED:
        addons[addon] = dict()
        addons[addon]["meta"] = get_meta(addon)
        addons[addon]["enabled"] = False
        
    
    context = {"addons":addons }
    return render_to_response("addons.html", context,
        context_instance=RequestContext(request))