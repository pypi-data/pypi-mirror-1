"""
app-media serve view

modified from http://www.djangosnippets.org/snippets/943/

thanks adamlofts

"""

import os
import mimetypes
from django.conf import settings
from django.shortcuts import Http404
from django.http import HttpResponse
from django.views.static import serve

from media_utils.settings import MEDIA_UTILS_PREPEND_LABEL_APPS, \
    MEDIA_UTILS_SKIP_APPS

def serve_app_media(request, path):
    """
    Serve static assets from media folders in all installed apps in
    development.

    To use, add a URL pattern such as:
        (r'^media/(?P<path>.+)$', 'media_utils.views.serve_app_media')

    Then the media in my_app/media will be available at media/
    as if it were overlayed on the files at MEDIA_ROOT (files at
    MEDIA_ROOT take precedence, then apps are checked in order of
    INSTALLED_APPS listing).  This is analogous to how app-templates
    work.

    IF an app does not place its media under an app_label/
    subdirectory, but its media should still be accessible at the
    media/app_label/ URL (rather than directly at media/), place the
    full import path of the app (exactly as listed in INSTALLED_APPS)
    in the MEDIA_UTILS_PREPEND_LABEL_APPS setting.  By default this is
    set to ('django.contrib.admin',).
    
    This view is intended for development purposes only and you should
    properly configure your webserver to serve media in production.
    
    """
    # first try to serve from project MEDIA_ROOT
    try:
        return serve(request, path=path, document_root=settings.MEDIA_ROOT)
    except Http404, err404:
        pass

    for app in settings.INSTALLED_APPS:
        if app in MEDIA_UTILS_SKIP_APPS:
            continue
        
        app_label = app.rsplit('.', 1)[-1]
        # Work out the directory in which this module resides
        mod = __import__(app, {}, {}, [app_label])
        moddir = os.path.dirname(mod.__file__)

        if app in MEDIA_UTILS_PREPEND_LABEL_APPS:
            try:
                (appname, new_path) = path.split('/', 1)
            except ValueError:
                appname = path
                new_path = ''
            if appname != app_label:
                continue
            abspath = os.path.join(moddir, 'media', new_path)
        else:
            abspath = os.path.join(moddir, 'media', path)
        if os.path.exists(abspath) and os.path.isfile(abspath):
            
            # Return the file as a response guessing the mimetype
            mimetype = mimetypes.guess_type(abspath)[0] or 'application/octet-stream'
            contents = open(abspath, 'rb').read()
            response = HttpResponse(contents, mimetype=mimetype)
            response["Content-Length"] = len(contents)
            return response
        
    # didn't find the file, raise the original 404
    raise err404

