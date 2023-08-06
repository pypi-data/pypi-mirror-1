from django import template
from django.utils.translation import gettext_lazy as _
import re

register = template.Library()

#
# Comparison filters come from:
#   http://code.djangoproject.com/wiki/BasicComparisonFilters
#
# expr tag comes from:
#   http://code.djangoproject.com/wiki/ExprTag
#

def eq(value, arg):
    """Returns a boolean of whether the value is equal to the argument"""
    return long(value) == long(arg)

def ne(value, arg):
    """Returns a boolean of whether the value is not equal to the argument"""
    return long(value) != long(arg)

def gt(value, arg):
    """Returns a boolean of whether the value is greater than the argument"""
    return long(value) > long(arg)

def lt(value, arg):
    """Returns a boolean of whether the value is less than the argument"""
    return long(value) < long(arg)

def gte(value, arg):
    """Returns a boolean of whether the value is greater than or equal to the argument"""
    return long(value) >= long(arg)

def lte(value, arg):
    """Returns a boolean of whether the value is less than or equal to the argument"""
    return long(value) <= long(arg)

def length_eq(value, arg):
    """Returns a boolean of whether the value's length is equal to than of the argument"""
    return len(value) == long(arg)

def length_ne(value, arg):
    """Returns a boolean of whether the value's length is not equal to than of the argument"""
    return len(value) != long(arg)

def length_gt(value, arg):
    """Returns a boolean of whether the value's length is greater than the argument"""
    return len(value) > long(arg)

def length_lt(value, arg):
    """Returns a boolean of whether the value's length is less than the argument"""
    return len(value) < long(arg)

def length_gte(value, arg):
    """Returns a boolean of whether the value's length is greater than or equal to the argument"""
    return len(value) >= long(arg)

def length_lte(value, arg):
    """Returns a boolean of whether the value's length is less than or equal to the argument"""
    return len(value) <= long(arg)

register.filter('eq', eq)
register.filter('ne', ne)
register.filter('gt', gt)
register.filter('lt', lt)
register.filter('gte', gte)
register.filter('lte', lte)
register.filter('ge', gte)
register.filter('le', lte)
register.filter('length_eq', length_eq)
register.filter('length_ne', length_ne)
register.filter('length_gt', length_gt)
register.filter('length_lt', length_lt)
register.filter('length_gte', length_gte)
register.filter('length_lte', length_lte)
register.filter('length_ge', length_gte)
register.filter('length_le', length_lte)


class ExprNode(template.Node):
    def __init__(self, expr_string, var_name):
        self.expr_string = expr_string
        self.var_name    = var_name

    def render(self, context):
        try:
            clist = list(context)
            clist.reverse()
            d = {}
            d['_'] = _
            for c in clist:
                d.update(c)
            if self.var_name:
                context[self.var_name] = eval(self.expr_string, d)
                return ''
            else:
                return str(eval(self.expr_string, d))
        except:
            raise

r_expr = re.compile(r'(.*?)\s+as\s+(\w+)', re.DOTALL)    
def do_expr(parser, token):
    """
    expr template tag

    Syntax:

    {% expr python_expression as variable_name %}
    {% expr python_expression %}

    (the second form will output the result to the template).

    Examples:

    {% expr "1" as var1 %}
    {% expr [0, 1, 2] as var2 %}
    {% expr _('Menu') as var3 %}
    {% expr var1 + "abc" as var4 %}

    {% expr 3 %}
    {% expr "".join(["a", "b", "c"]) %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents[0]
    m = r_expr.search(arg)
    if m:
        expr_string, var_name = m.groups()
    else:
        if not arg:
            raise template.TemplateSyntaxError, "%r tag at least require one argument" % tag_name
            
        expr_string, var_name = arg, None
    return ExprNode(expr_string, var_name)
do_expr = register.tag('expr', do_expr)
