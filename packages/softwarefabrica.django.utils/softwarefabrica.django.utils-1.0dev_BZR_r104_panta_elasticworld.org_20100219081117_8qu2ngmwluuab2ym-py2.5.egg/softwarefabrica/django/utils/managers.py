# managers.py
# Copyright (C) 2009 Marco Pantaleoni. All rights reserved
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

from django.db import models

class QuerySetManager(models.Manager):
    """
    A model manager using the model QuerySet.
    This allows chaining of extended filtering methods through the model manager,
    as described in http://simonwillison.net/2008/May/1/orm/

    Simply use an instance of this class as the (default) model manager, and
    add a QuerySet subclass (named ``QuerySet``) inside the model class defining
    all the methods that you need supported by the manager.
    
    For a detailed explanation, please see:

    http://simonwillison.net/2008/May/1/orm/
    """
    def get_query_set(self):
        return self.model.QuerySet(self.model)
