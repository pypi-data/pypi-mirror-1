# paginator template tag
# from:
#  http://www.djangosnippets.org/snippets/73/
#
# see also:
#  http://www.djangosnippets.org/snippets/208/
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

from django import template

from softwarefabrica.django.utils.templates import CachedTemplateLibrary

#register = template.Library()
register = CachedTemplateLibrary()

def paginator(context, url="", adjacent_pages=5,
              paginator_object_name='paginator',
              page_object_name='page_obj'):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    @see: http://www.djangosnippets.org/snippets/73/
    @see: http://www.djangosnippets.org/snippets/208/
    """

    paginator = None
    page_obj  = None
    if context.has_key(paginator_object_name):
        paginator = context[paginator_object_name]
    if context.has_key(page_object_name):
        page_obj = context[page_object_name]

    if not (paginator and page_obj):
        return {
            'is_paginated': False,
            'paginator': None,
            }

    page_numbers = [n for n in \
                    range(page_obj.number - adjacent_pages, page_obj.number + adjacent_pages + 1) \
                    if n > 0 and n <= paginator.num_pages]

    res = {
        'is_paginated': True,
        'paginator': paginator,
        'page_obj': page_obj,
        'url': url,
        'page_numbers': page_numbers,
        'show_first': 1 not in page_numbers,
        'show_last': paginator.num_pages not in page_numbers,
    }

    keys = ("is_paginated", "hits", "results_per_page", "page", "pages",
            "next", "previous", "has_next", "has_previous",
            "first_on_page", "last_on_page", "page_range",
            "paginator", "page_obj", "is_popup",
            paginator_object_name, page_object_name)
    for k in keys:
        if k in context:
            res.update({k: context[k]})

    return res

register.inclusion_tag('utils/paginator.html', takes_context=True)(paginator)
