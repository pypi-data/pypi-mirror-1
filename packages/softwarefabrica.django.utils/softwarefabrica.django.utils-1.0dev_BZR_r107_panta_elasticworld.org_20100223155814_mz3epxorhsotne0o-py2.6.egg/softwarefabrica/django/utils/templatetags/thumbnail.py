"""
Simple thumbnail template filter.

Based on http://www.djangosnippets.org/snippets/955/

Modifications are:

Copyright (C) 2010 Marco Pantaleoni. All rights reserved.
"""

# based on http://www.djangosnippets.org/snippets/955/

import os
try:
    from PIL import Image
except:
    import Image

from django import template

register = template.Library()

def thumbnail(imagefile, size='104x104'):
    # obtain the size
    x, y = [int(x) for x in size.split('x')]

    # define the filename and the miniature filename
    imagefile_dirname, imagefile_filename = os.path.split(imagefile.path)
    imagefile_basename, imagefile_format = os.path.splitext(imagefile_filename)

    miniature_dirname  = imagefile_dirname
    miniature_filename = '_thumb_' + imagefile_basename + '_' + size + imagefile_format
    miniature_pathname = os.path.join(miniature_dirname, miniature_filename)

    imagefile_url_dirname, imagefile_url_filename = os.path.split(imagefile.url)
    miniature_url = imagefile_url_dirname + '/' + miniature_filename

    if os.path.exists(miniature_pathname) and os.path.getmtime(imagefile.path) > os.path.getmtime(miniature_pathname):
        os.unlink(miniature_pathname)

    if not os.path.exists(miniature_pathname):
        image = Image.open(imagefile.path)
        # Convert to RGB if necessary
        # Thanks to Limodou on DjangoSnippets.org
        # http://www.djangosnippets.org/snippets/20/
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')

        image.thumbnail([x, y], Image.ANTIALIAS)
        try:
            image.save(miniature_pathname, image.format, quality=90, optimize=1)
        except:
            image.save(miniature_pathname, image.format, quality=90)

    return miniature_url

register.filter(thumbnail)
