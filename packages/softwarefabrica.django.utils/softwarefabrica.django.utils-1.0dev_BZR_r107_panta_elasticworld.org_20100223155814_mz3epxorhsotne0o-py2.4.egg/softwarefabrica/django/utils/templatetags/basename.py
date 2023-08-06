"""
'basename' template filter.

Return the filename component of a full path.

Copyright (C) 2010 Marco Pantaleoni. All rights reserved.
"""

import os
from django import template

register = template.Library()

def basename(pathname):
    return os.path.basename(pathname)
register.filter(basename)
