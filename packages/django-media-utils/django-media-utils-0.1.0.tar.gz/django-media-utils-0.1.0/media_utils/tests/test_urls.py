from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'^media/(?P<path>.+)$', 'media_utils.views.serve_app_media')
    )
