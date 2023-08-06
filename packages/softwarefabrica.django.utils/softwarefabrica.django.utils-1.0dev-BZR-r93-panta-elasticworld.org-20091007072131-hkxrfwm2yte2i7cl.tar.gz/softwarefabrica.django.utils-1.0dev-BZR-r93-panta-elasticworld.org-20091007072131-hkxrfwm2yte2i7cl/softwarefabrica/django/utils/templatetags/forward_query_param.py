from django import template
from django.utils.html import conditional_escape, escape
from django.utils.safestring import mark_safe

register = template.Library()

# based on:
#   http://groups.google.it/group/django-users/browse_thread/thread/29c3eb3d80e9b78a?hl=it&ie=UTF-8&oe=utf-8&q=paging_control+django-users#df55b3715e2f8d91
#   http://www.mail-archive.com/django-users%40googlegroups.com/msg01730.html
#   http://osdir.com/ml/python.django.user/2005-11/msg00512.html

class ForwardQueryParamNode(template.Node):
    def __init__(self, param_name):
        self.param_name = param_name
 
    def render(self, context):
        request = None
        try:
            request = context['request']
        except:
            request = context['pagevars'].request
        result = '<div><input type="hidden" name="' + self.param_name + \
               '" value="' + escape(request.GET.get(self.param_name, '')) + \
               '" /></div>'
        return mark_safe(result)
 
# forward_query_param - turn a param in query string into a hidden
# input field. Needs to be able to get the request object from the context
def do_forward_query_param(parser, token):
    """
    Turns a parameter in a query string into a hidden input field,
    allowing it to be 'forwarded' as part of the next request in
    a form submission. It requires one argument (the name of the parameter),
    and also requires that the request object be in the context as 
    directly under the ``request`` name or by putting the standard
    ``pagevars`` object in the context.
    """
    try:
        tag_name, param_name = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, \
              "forward_query_param tag requires an argument"
    param_name = param_name.strip('"')
    return ForwardQueryParamNode(param_name)

register.tag('forward_query_param', do_forward_query_param)
