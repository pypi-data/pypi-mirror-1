==================
django-media-utils
==================

Utilities for managing static files in Django projects.

The ``serve_app_media`` view
============================

Serve static assets from media folders in all installed apps in development.

To use, add something like this to your root URLconf::

    if DEBUG:
        (r'^media/(?P<path>.+)$', 'media_utils.views.serve_app_media')

The files in my_app/media/ will then be available at the media/ URL as if
they were located at MEDIA_ROOT.  Files actually at MEDIA_ROOT take
precedence, then apps are checked in order of INSTALLED_APPS listing.  This
is analogous to the ``app_directories`` template loader.

A common convention is to place your app's static files under
my_app/media/my_app/, in which case they will be served at the URL
/media/my_app/.

This view is intended for use in development only.  Properly configure your
webserver to serve media in production (see the ``link_media`` management
command below).

The ``link_media`` management command
=====================================
    
When you move your site into production, you will want your webserver to
serve static files directly off the filesystem, not through Django.  If you
have media in several reusable apps, it can be a pain to manually set up
symlinks or webserver alias directives to mimic the functionality of the
``serve_app_media`` view.

The ``link_media`` management command automatically creates symbolic links
to all your media files, including files in application directories, from a
webserver directory that you specify.  For instance::

    ./manage.py link_media /var/www/my_site_media

This will create symbolic links in the my_site_media pointing to all of your
static files. Name clashes are resolved with the same priority order as in
the ``serve_app_media`` view: files in the project MEDIA_ROOT take
precedence, followed by app files in INSTALLED_APPS order.

``link_media`` is non-destructive by default: it will not remove or alter
existing files or symbolic links in the specified directory.  If you pass it
the ``--clean`` option, it will first remove all files and subdirectories in
the specified directory before creating its symbolic links.  Be careful with
this option!

Obviously this command is only useful on operating systems which support
symbolic links.
