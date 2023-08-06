# -*- coding: utf-8 -*-

"""
installs except.py client as 500 handler for django application

needs EXCEPT_PY_API_KEY and EXCEPT_PY_SERVER in settings.py
"""

import os

from django.conf import settings
from django.utils.importlib import import_module
from django.http import HttpResponseServerError
from django.template import Context, RequestContext, loader


__all__ = ('server_error', )


assert settings.EXCEPT_PY_API_KEY, 'EXCEPT_PY_API_KEY not found in settings'
assert settings.EXCEPT_PY_SERVER, 'EXCEPT_PY_SERVER not found in settings'

MODE = getattr(settings, 'EXCEPT_PY_MODE', 'http')

os.environ['EXCEPT_PY_API_KEY'] = settings.EXCEPT_PY_API_KEY
os.environ['EXCEPT_PY_SERVER'] = settings.EXCEPT_PY_SERVER


from except_py_client.client import send_exception


def server_error(request, template_name='500.html'):
    """
    handles unhandled exception, sends information to except.py service
    and renders 500.html template just like
    django.views.defaults.server_error does
    """
    
    meta = {
        'url': request.get_full_path(),
        'method': request.method,
    }
    
    if request.user.is_authenticated():
        if request.user.email:
            user = u'%s <%s>' % (request.user, request.user.email)
        else:
            user = unicode(request.user)
        meta['user'] = user        
    
    if request.GET:
        GET = {}
        for key in request.GET.keys():
            GET[key] = request.GET.getlist(key)
        meta['GET'] = GET
    
    send_exception(_mode=MODE, **meta)
    
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(Context({})))


urlconf = import_module(settings.ROOT_URLCONF)
urlconf.handler500 = 'except_py_client.django.server_error'
