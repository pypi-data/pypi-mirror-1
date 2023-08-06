from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe
from softwarefabrica.django.utils.viewshelpers import static_media_prefix

register = template.Library()

def do_sitevars(parser, token):
    return SitevarsNode()

class SitevarsNode(template.Node):
    def render(self, context):
        var_basesite = None
        var_domain   = ''
        settings_members = []
        if hasattr(settings, '__dir__'):
            settings_members = dir(settings)
        elif hasattr(settings, 'get_all_members'):
            settings_members = settings.get_all_members()
        if 'SITE_ID' in settings_members:
            var_basesite = Site.objects.get_current()
            var_domain	 = var_basesite.domain
        staticmedia     = static_media_prefix()
        var_js          = staticmedia + '/js'
        var_images      = staticmedia + '/images'
        var_staticmedia = staticmedia
        var_uploadmedia = settings.MEDIA_URL # same as settings.MEDIA_URL / settings.UPLOAD_MEDIA_URL
        var_adminmedia  = settings.ADMIN_MEDIA_PREFIX
        if var_adminmedia[-1] == '/':
            var_adminmedia = var_adminmedia[:-1] # strip trailing '/'
        context['basesite'] = mark_safe(var_basesite)
        context['domain']   = mark_safe(var_domain)
        context['static']   = mark_safe(var_staticmedia)
        context['upload']   = mark_safe(var_uploadmedia)
        context['admin']    = mark_safe(var_adminmedia)
        context['images']   = mark_safe(var_images)
        context['js']       = mark_safe(var_js)
        return ''

register.tag('sitevars', do_sitevars)
