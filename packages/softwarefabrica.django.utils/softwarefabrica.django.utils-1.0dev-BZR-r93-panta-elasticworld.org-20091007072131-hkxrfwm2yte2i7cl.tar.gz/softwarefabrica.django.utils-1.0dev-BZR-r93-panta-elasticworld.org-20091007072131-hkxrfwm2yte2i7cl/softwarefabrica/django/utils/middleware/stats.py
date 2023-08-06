"""
Performance statistics middleware

To use this middleware, in settings.py you need to set:

DEBUG_STATS   = True

MIDDLEWARE_CLASSES = (
    ...
    'softwarefabrica.django.utils.middleware.stats.StatsMiddleware',
    ...)
"""

# see:
#   http://code.djangoproject.com/wiki/PageStatsMiddleware
#   http://www.djangosnippets.org/snippets/161/
#   http://www.djangosnippets.org/snippets/344/
#
# Modified by: Marco Pantaleoni

import time
from operator import add
import re

from django.conf import settings
from django.db import connection

class StatsMiddleware(object):
    """
    Statistics middleware.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # turn on debugging in db backend to capture time
        from django.conf import settings

        debug_stats = getattr(settings, "DEBUG_STATS", False)

        if not debug_stats:
            return view_func(request, *view_args, **view_kwargs)

        debug = settings.DEBUG
        settings.DEBUG = True

        # get number of db queries before we do anything
        n = len(connection.queries)

        # time the view
        start = time.time()
        response = view_func(request, *view_args, **view_kwargs)
        totTime = time.time() - start

        # compute the db time for the queries just run
        queries = len(connection.queries) - n
        if queries:
            dbTime = reduce(add, [float(q['time']) 
                                  for q in connection.queries[n:]])
        else:
            dbTime = 0.0

        # and backout python time
        pyTime = totTime - dbTime

        # restore debugging setting again
        settings.DEBUG = debug

        stats = {
            'totTime': totTime,
            'pyTime': pyTime,
            'dbTime': dbTime,
            'queries': queries,
            }

        # replace the comment if found
        content_type = None
        if response.has_header('Content-Type'):
            content_type = response['Content-Type']
        if response and response.content and content_type.startswith('text/html'):
            s = response.content
            regexp = re.compile(r'(?P<cmt><!--\s*STATS:(?P<fmt>.*?)-->)')
            match = regexp.search(s)
            if match:
                s = s[:match.start('cmt')] + \
                    match.group('fmt') % stats + \
                    s[match.end('cmt'):]
                response.content = s
        else:
            print stats

        return response
