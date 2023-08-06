# urlsave template tag
#
# Based on django 'url' template tag.
#
# Modifications on the original are:
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

from django.template import Node, NodeList, Template, Context, Variable
from django.template import TemplateSyntaxError, VariableDoesNotExist, BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END, SINGLE_BRACE_START, SINGLE_BRACE_END, COMMENT_TAG_START, COMMENT_TAG_END
from django.template import get_library, Library, InvalidTemplateLibrary

register = Library()

class URLSaveNode(Node):
    def __init__(self, view_name, args, kwargs, saveto):
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.saveto = saveto

    def render(self, context):
        from django.core.urlresolvers import reverse, NoReverseMatch
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])
        try:
            res = reverse(self.view_name, args=args, kwargs=kwargs)
            context[self.saveto] = res
            return ''
        except NoReverseMatch:
            try:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                res = reverse(project_name + '.' + self.view_name,
                              args=args, kwargs=kwargs)
                context[self.saveto] = res
                return ''
            except NoReverseMatch:
                context[self.saveto] = ''
                return ''

def urlsave(parser, token):
    """
    Like django 'url' template tag, but saves the result into a context
    variable.

        {% urlsave path.to.some_view arg1,arg2,name1=value1 as myvar %}

    """
    bits = token.contents.split(' ', 4)
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    args = []
    kwargs = {}
    saveto = 'url'
    if len(bits) > 2:
        if bits[2] == 'as':
            saveto = bits[3]
        else:
            for arg in bits[2].split(','):
                if '=' in arg:
                    k, v = arg.split('=', 1)
                    k = k.strip()
                    kwargs[k] = parser.compile_filter(v)
                else:
                    args.append(parser.compile_filter(arg))
            if (len(bits) > 3) and (bits[3] == 'as'):
                saveto = bits[4]
    return URLSaveNode(bits[1], args, kwargs, saveto)
urlsave = register.tag(urlsave)
