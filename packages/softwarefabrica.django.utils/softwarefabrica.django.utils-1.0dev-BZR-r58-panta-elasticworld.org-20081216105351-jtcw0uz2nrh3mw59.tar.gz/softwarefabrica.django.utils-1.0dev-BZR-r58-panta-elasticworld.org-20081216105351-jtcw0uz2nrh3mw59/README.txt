softwarefabrica.django.utils library
====================================

This library provides many useful routines and abstractions for applications
developed with the `Django`_ web framework.

Don't forget to check also our other `Django`_ applications,
``softwarefabrica.django.forms``, and ``softwarefabrica.django.crud``.

.. _`Django`: http://www.djangoproject.com


*Marco Pantaleoni*

.. contents::

PRE-REQUISITES
--------------

This library depends on the ``sflib`` library from the same author.
If you use the EasyInstall_ outlined below, dependencies will be satisfied
automatically (the ``easy_install`` will take care of everything).

INSTALLATION
------------

You can download and install the most up-to-date version in one step
using EasyInstall_. For example, on a unix-like system:

::

  $ su
  # easy_install softwarefabrica.django.utils

If you are using Ubuntu, to install system-wide:

::

  $ sudo easy_install softwarefabrica.django.utils

Otherwise you can just download the source package (eg. from PyPI_),
extract it and run the usual ``setup.py`` commands:

::

  $ su
  # python setup.py install

Then you can use the library in any django project by simple including it in the
``INSTALLED_APPS`` settings variable, as outlined below.

.. _EasyInstall: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _PyPI: http://pypi.python.org/pypi

DOWNLOAD
--------

If you don't want or cannot install using EasyInstall_, download the
package from Cheese Shop:

  http://cheeseshop.python.org/pypi/softwarefabrica.django.utils/

In a future, it will be possible to download also from:

  http://www.softwarefabrica.org/projects/softwarefabrica.django.utils/

Using the forms library in your applications
--------------------------------------------

Once you've installed the library and want to use it in your Django
applications, simply put ``'softwarefabrica.django.utils'`` in your
``INSTALLED_APPS`` setting.

Since there are no associated models, a ``manage.py syncdb`` command is not
necessary.

That's it!

DOCUMENTATION
-------------

Documentation is included in the form of *docstrings*, inside the library source
code.

CONTACTS
--------

It's possible to contact the author by e-mail at the following addresses:

  m.pantaleoni at softwarefabrica.org

  panta at elasticworld.org

  marco.pantaleoni at gmail.com


LICENSE
-------

This software is covered by the GNU General Public License version 2.
If you want to use this software in a closed source application, you
need to buy a commercial license from the author.

This open source version is:

    Copyright (C) 2007-2008  Marco Pantaleoni. All rights reserved.

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License version 2 as
    published by the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
