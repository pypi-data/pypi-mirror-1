# viewshelpers.py
#
# Copyright (C) 2007-2008 Marco Pantaleoni. All rights reserved
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Views helper functions.
"""

from django.template  import RequestContext
import django.shortcuts
from django.contrib.sites.models import Site

from django.http import HttpRequest, HttpResponse
from django.db.models.query import QuerySet
from django.core import serializers
import simplejson

from django.conf import settings

from softwarefabrica.django.utils.templates import cached_template_render_to_string

# ------------------------------------------------------------------------
#   GLOBALS
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
#   CONTEXT PROCESSORS
# ------------------------------------------------------------------------

def static_media_prefix():
    staticmedia = None
    try:
        staticmedia = settings.STATIC_MEDIA_PREFIX
    except:
        try:
            staticmedia = settings.STATIC_URL
        except:
            pass
    if staticmedia == None:
        staticmedia = "/static"     # we are desperate, shot in the dark...
    if (staticmedia != "/") and (staticmedia[-1] == "/"):
        staticmedia = staticmedia[:-1]
    return staticmedia

def static_media_images_prefix():
    staticmedia = static_media_prefix()
    return staticmedia + '/images'

def static_media_js_prefix():
    staticmedia = static_media_prefix()
    return staticmedia + '/js'

def context_vars(request):
    """
    Context processor populating common portal variables.

    Determine context variables for the site's base template.
    This will be pulled in by the templates through the context processor
    mechanism, so we don't need to call it directly.
    (It need to be added to TEMPLATE_CONTEXT_PROCESSORS settings variable).
    """
    var_basesite = None
    var_domain   = ''
    settings_members = []
    if hasattr(settings, '__dir__'):
        settings_members = dir(settings)
    elif hasattr(settings, 'get_all_members'):
        settings_members = settings.get_all_members()
    if 'SITE_ID' in settings_members:
        var_basesite = Site.objects.get_current()
        var_domain   = var_basesite.domain
    staticmedia = static_media_prefix()
    var_js          = staticmedia + '/js'
    var_images      = staticmedia + '/images'
    var_staticmedia = staticmedia
    var_uploadmedia = settings.MEDIA_URL # same as settings.MEDIA_URL / settings.UPLOAD_MEDIA_URL
    var_adminmedia  = settings.ADMIN_MEDIA_PREFIX
    if var_adminmedia[-1] == '/':
        var_adminmedia = var_adminmedia[:-1] # strip trailing '/'
    return {
        'basesite': var_basesite,
        'domain'  : var_domain,
        'static'  : var_staticmedia,
        'upload'  : var_uploadmedia,
        'admin'   : var_adminmedia,
        'images'  : var_images,
        'js'      : var_js,
        }

# ------------------------------------------------------------------------
#   VIEW UTILITY FUNCTIONS
# ------------------------------------------------------------------------

def cached_template_render_to_response(*args, **kwargs):
    """
    A version of django.shortcuts.render_to_response that caches compiled templates.

    Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    return HttpResponse(cached_template_render_to_string(*args, **kwargs), **httpresponse_kwargs)

def request_render_to_response(request, *args, **kwargs):
    context_instance = kwargs.get('context_instance', None)
    context_instance = context_instance or RequestContext(request)
    kwargs['context_instance'] = context_instance
    return cached_template_render_to_response(*args, **kwargs)

#def render_to_response(request, template, dictionary=None, mimetype=None, context_instance=None):
#    dictionary       = dictionary or {}
#    context_instance = context_instance or RequestContext(request)
#
#    if mimetype is None:
#        return django.shortcuts.render_to_response(template, dictionary, context_instance=context_instance)
#    return django.shortcuts.render_to_response(template, dictionary, mimetype=mimetype, context_instance=context_instance)

render_to_response = request_render_to_response

def json_response(request, data, *args, **kwargs):
    "AJAX - return provided data in a JSON serialized response."
    #logging.debug("data: %s" % repr(data))
    if isinstance(data, QuerySet):
        serialized = serializers.serialize("json", data, *args, **kwargs)
    else:
        serialized = simplejson.dumps(data)
    #logging.debug("serialized: %s" % repr(serialized))
    return HttpResponse(serialized, mimetype="application/javascript")
