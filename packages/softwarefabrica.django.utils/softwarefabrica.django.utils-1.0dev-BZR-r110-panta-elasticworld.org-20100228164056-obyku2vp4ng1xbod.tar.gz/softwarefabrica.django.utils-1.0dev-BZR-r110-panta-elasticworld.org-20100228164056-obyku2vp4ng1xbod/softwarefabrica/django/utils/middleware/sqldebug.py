"""
SQL debugging middleware.

To use this middleware, in settings.py you need to set:

DEBUG_SQL = True

# Since you can't see the output if the page results in a redirect,
# you can log the result into a directory:
# DEBUG_SQL = '/mypath/...'

MIDDLEWARE_CLASSES = (
    ...
    'softwarefabrica.django.utils.middleware.sqldebug.SQLDebugMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    ...)

"""

# Modified by: Marco Pantaleoni

import os
import time
import datetime

from django.conf import settings
from django.db import connection
from django.template import Template, Context

class SQLDebugMiddleware:
    """
    SQL debugging middleware.

    This middleware appends to the output page a table reporting the SQL queries
    executed and the time spent in each of them.
    Repeated queries are reported as well.
    """

    start = None

    def process_request(self, request):
        self.start = time.time()

    def process_response ( self, request, response ):
        # self.start is empty if an append slash redirect happened.
        debug_sql = getattr(settings, "DEBUG_SQL", False)
        if (not self.start) or not debug_sql:
            return response

        timesql = 0.0
        for q in connection.queries:
            timesql += float(q['time'])

        seen      = {}
        duplicate = 0
        for q in connection.queries:
            sql = q["sql"]
            c = seen.get(sql, 0)
            if c:
                duplicate += 1
            q["seen"] = c
            seen[sql] = c+1

        t = Template('''
                     <p>
                     <em>request.path:</em> {{ request.path|escape }}<br />
                     <em>Total query count:</em> {{ queries|length }}<br/>
                     <em>Total duplicate query count:</em> {{ duplicate }}<br/>
                     <em>Total SQL execution time:</em> {{ timesql }}<br/>
                     <em>Total Request execution time:</em> {{ timerequest }}<br/>
                     </p>
                     <table class="sqllog">
                       <tr>
                         <th>Time</th>
                         <th>Seen</th>
                         <th>SQL</th>
                       </tr> 
                       {% for sql in queries %}
                       <tr class="{% cycle 'odd' 'even' %}">
                         <td>{{ sql.time }}</td>
                         <td align="right">{{ sql.seen }}</td>
                         <td>{{ sql.sql }}</td>
                       </tr> 
                       {% endfor %}
                     </table>
                     ''')
        timerequest = round(time.time() - self.start, 3)
        queries     = connection.queries
        c_dict = dict(request     = request,
                      queries     = queries,
                      duplicate   = duplicate,
                      timesql     = timesql,
                      timerequest = timerequest)
        logtext = t.render(Context(c_dict))

        if debug_sql == True:
            content_type = response.get('Content-Type', "")
            if response and response.content and content_type.startswith('text/html'):
                #response.content = "%s%s" % ( response.content, logtext )
                content = response.content.decode('utf-8')
                content += logtext
                response.content = content.encode('utf-8')
            return response
        elif debug_sql and os.path.isdir(debug_sql):
            outfile = os.path.join(debug_sql, "%s.html" % datetime.datetime.now().isoformat())
            fd = open(outfile, "wt")
            fd.write('''<html><head><title>SQL Log %s</title></head><body>%s</body></html>''' % (request.path, logtext))
            fd.close()
        elif debug_sql:
            print logtext
        return response
