====================
Emencia django admin
====================

This is a package that add some features on the django admin interface.

This features are:
    - delete function on the list view
    - csv export

A part of the csv export was taken from the libcommonDjango of Pimentech
(http://garage.pimentech.net/libcommonDjango_documentation_API/)

Installation
============

Source Distribution
-------------------

Download the archive distribution file and unpack it. From within the extracted directory run the following command::

   python setup.py install


Tracking the Development Version
--------------------------------

The current development version of Emencia Django Admin can be checked out via Subversion from the project site using the following command::

    svn checkout http://svn.emencia.net/repo/public/django_apps/emencia_django_admin/trunk emencia_django_admin

Install the package like the source Distribution

You can verify Emencia django admin is available to your project by running the following commands from within your project directory::

    manage.py shell

    >>> import emencia_django_admin
    >>> emencia_django_admin.__VERSION__
    '0.1'


Configure Your Django Settings
------------------------------

Add 'Emencia django admin' to your INSTALLED_APPS setting::

    INSTALLED_APPS = (
         # ...other installed applications,
         'emencia_django_admin',
    )

Add these rules on the urls.py of your project (before the admin line)::

    (r'^admin/([^/]+)/([^/]+)/delete/$', 'emencia_django_admin.admin.delete'),
    (r'^admin/([^/]+)/([^/]+)/csv/$', 'emencia_django_admin.admin.csv_form'),
    (r'^admin/(.*)', admin.site.root),
