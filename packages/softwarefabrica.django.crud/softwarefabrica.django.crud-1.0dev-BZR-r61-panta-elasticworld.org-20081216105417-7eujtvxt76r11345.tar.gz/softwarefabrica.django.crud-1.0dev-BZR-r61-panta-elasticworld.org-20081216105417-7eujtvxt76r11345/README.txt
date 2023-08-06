softwarefabrica.django.crud library
===================================

This library provides flexible and advanced CRUD generic views for applications
developed with the `Django`_ web framework.

By default the generic views make use of the advanced form classes made
available through `softwarefabrica.django.forms`, thus automatically using
the optional template-based form rendering, the advanced widgets for date,
time, foreign-key and many-to-many fields, etc.
However it's easy to switch back to `Django`_ default forms and widgets if
desired.

Generic views are a drop-in replacement for those offered by `Django`_, it's just a
matter of importing them from `softwarefabrica.django.crud.crud` instead of from
`django.views.generic`.
In addition, a more flexible set of Object Oriented views is available.
Just subclass them as you like, instantiate them and put the instances inside
your URLconf, as if they were regular function views.
In the majority of cases you won't even need to subclass them, since you can go
a long way just passing the proper parameters to the constructor.

In fact, Object oriented views are so powerful and flexible that plain
functional views are actually instances. They are implemented by the library in
this way:

::

  create_object = CreateObjectView()
  update_object = UpdateObjectView()
  delete_object = DeleteObjectView()
  object_detail = DetailObjectView()
  object_list   = ListObjectView()


Please see the documentation for more information and examples.

Don't forget to check also our other `Django`_ applications,
``softwarefabrica.django.utils``, and ``softwarefabrica.django.forms``.

Happy coding!

.. _`Django`: http://www.djangoproject.com
.. _`forms library`: http://docs.djangoproject.com/en/dev/topics/forms/


*Marco Pantaleoni*

.. contents::

PRE-REQUISITES
--------------

This library depends on the `sflib`, `softwarefabrica.django.utils` and
`softwarefabrica.django.forms` libraries from the same author.
If you use the EasyInstall_ outlined below, dependencies will be satisfied
automatically (the ``easy_install`` will take care of everything).

INSTALLATION
------------

You can download and install the most up-to-date version in one step
using EasyInstall_. For example, on a unix-like system:

::

  $ su
  # easy_install softwarefabrica.django.crud

If you are using Ubuntu, to install system-wide:

::

  $ sudo easy_install softwarefabrica.django.crud

Otherwise you can just download the source package (eg. from PyPI_),
extract it and run the usual ``setup.py`` commands:

::

  $ su
  # python setup.py install

Then you can use the library in any django project by simple including it in the
``INSTALLED_APPS`` settings variable, as outlined below. Remember also to
include the aforementioned dependencies (with the exception of `sflib`, which is
not a django application).

.. _EasyInstall: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _PyPI: http://pypi.python.org/pypi

DOWNLOAD
--------

If you don't want or cannot install using EasyInstall_, download the
package from Cheese Shop:

  http://cheeseshop.python.org/pypi/softwarefabrica.django.crud/

In a future, it will be possible to download also from:

  http://www.softwarefabrica.org/projects/softwarefabrica.django.crud/

Using the CRUD generic views library in your applications
---------------------------------------------------------

Once you've installed the library and want to use it in your Django
applications, simply put ``'softwarefabrica.django.crud'`` in your
``INSTALLED_APPS`` setting, after its dependencies
(``'softwarefabrica.django.utils'`` and ``'softwarefabrica.django.forms'``).

Since there are no associated models, a ``manage.py syncdb`` command is not
necessary.

That's it!

DOCUMENTATION
-------------

Documentation is included in the form of *docstrings*, inside the library source
code.

For some advanced examples, please see also the included automatic tests.

TESTING
-------

The library includes automatic tests.
To run the tests, do:

::

  $ export DJANGO_SETTINGS_MODULE=softwarefabrica.django.crud.tests.settings
  $ django-admin.py test

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
