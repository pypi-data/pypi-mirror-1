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

register = template.Library()

def paginator(context, url="", adjacent_pages=5, template_object_name='object'):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    @see: http://www.djangosnippets.org/snippets/73/
    @see: http://www.djangosnippets.org/snippets/208/
    """

    template_object_list_name = '%s_list' % template_object_name
    #s = max(1, context["page"] - adjacent_pages - max(0, context["page"]+adjacent_pages-context["pages"]))
    #page_numbers = range(s, min(context["pages"], s+2*adjacent_pages)+1)

    page_numbers = [n for n in \
                    range(context['page'] - adjacent_pages, context['page'] + adjacent_pages + 1) \
                    if n > 0 and n <= context['pages']]
    results_this_page = context[template_object_list_name].__len__()
    range_base = ((context['page'] - 1) * context['results_per_page'])

    res = {
        'url': url,
        'results_this_page': results_this_page,
        'first_this_page': range_base + 1,
        'last_this_page': range_base + results_this_page,
        'page_numbers': page_numbers,
        'show_first': 1 not in page_numbers,
        'show_last': context['pages'] not in page_numbers,
    }

    keys = ("is_paginated", "hits", "results_per_page", "page", "pages", "next", "previous", "has_next", "has_previous", "first_on_page", "last_on_page", "page_range", "paginator", "page_obj", "is_popup",)
    for k in keys:
        res.update({k: context[k]})

    return res

register.inclusion_tag('utils/paginator.html', takes_context=True)(paginator)
