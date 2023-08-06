from django import template
from django.template.context import Context

# ------------------------------------------------------------------------
#   GLOBALS
# ------------------------------------------------------------------------

_template_cache = {}

# ------------------------------------------------------------------------
#   CODE
# ------------------------------------------------------------------------

def cached_template_get_template(template_name, cache_template=True):
    """
    A version of django.template.loader.get_template() that caches compiled
    templates.

    Returns a compiled Template object for the given template name,
    handling template inheritance recursively.
    """
    global _template_cache

    if isinstance(template_name, (list, tuple)):
        t_id = tuple(template_name)
    else:
        t_id = template_name
    if cache_template and (t_id in _template_cache):
        return _template_cache[t_id]

    from django.template.loader import get_template

    t = get_template(template_name)
    _template_cache[t_id] = t
    return t

def cached_template_select_template(template_name_list, cache_template=True):
    """
    A version of django.template.loader.select_template() that caches compiled
    templates.

    Given a list of template names, returns the first that can be loaded.
    """

    global _template_cache

    if isinstance(template_name_list, (list, tuple)):
        t_id = tuple(template_name_list)
    else:
        t_id = template_name_list
    if cache_template and (t_id in _template_cache):
        return _template_cache[t_id]

    from django.template.loader import select_template

    t = select_template(template_name_list)
    _template_cache[t_id] = t
    return t

def cached_template_render_to_string(template_name, dictionary=None, context_instance=None, cache_template=True):
    """
    A version of django.template.loader.render_to_string() that caches compiled
    templates.

    Loads the given template_name and renders it with the given dictionary as
    context. The template_name may be a string to load a single template using
    get_template, or it may be a tuple to use select_template to find one of
    the templates in the list. Returns a string.
    """
    global _template_cache

    from django.template import Context

    dictionary = dictionary or {}
    if isinstance(template_name, (list, tuple)):
        t_id = tuple(template_name)
    else:
        t_id = template_name
    if cache_template and (t_id in _template_cache):
        t = _template_cache[t_id]
    else:
        if isinstance(template_name, (list, tuple)):
            t = select_template(template_name)
        else:
            t = get_template(template_name)
        _template_cache[t_id] = t
    if context_instance:
        context_instance.update(dictionary)
    else:
        context_instance = Context(dictionary)
    return t.render(context_instance)

get_template     = cached_template_get_template
select_template  = cached_template_select_template
render_to_string = cached_template_render_to_string

class CachedTemplateLibrary(template.Library):
    def inclusion_tag(self, file_name, context_class=Context, takes_context=False):
        from inspect import getargspec
        from django.template import TemplateSyntaxError, Variable, Node, generic_tag_compiler
        from django.utils.itercompat import is_iterable
        from django.utils.functional import curry

        def dec(func):
            params, xx, xxx, defaults = getargspec(func)
            if takes_context:
                if params[0] == 'context':
                    params = params[1:]
                else:
                    raise TemplateSyntaxError("Any tag function decorated with takes_context=True must have a first argument of 'context'")

            class InclusionNode(Node):
                def __init__(self, vars_to_resolve):
                    self.vars_to_resolve = map(Variable, vars_to_resolve)

                def render(self, context):
                    resolved_vars = [var.resolve(context) for var in self.vars_to_resolve]
                    if takes_context:
                        args = [context] + resolved_vars
                    else:
                        args = resolved_vars

                    dict = func(*args)

                    if not getattr(self, 'nodelist', False):
                        from django.template.loader import get_template, select_template
                        if not isinstance(file_name, basestring) and is_iterable(file_name):
                            t = cached_template_select_template(file_name)
                        else:
                            t = cached_template_get_template(file_name)
                        self.nodelist = t.nodelist
                    return self.nodelist.render(context_class(dict,
                            autoescape=context.autoescape))

            compile_func = curry(generic_tag_compiler, params, defaults, getattr(func, "_decorated_function", func).__name__, InclusionNode)
            compile_func.__doc__ = func.__doc__
            self.tag(getattr(func, "_decorated_function", func).__name__, compile_func)
            return func
        return dec
