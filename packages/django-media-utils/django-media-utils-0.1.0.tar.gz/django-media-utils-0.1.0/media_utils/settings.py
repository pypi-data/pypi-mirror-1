"""
settings for media_utils

"""
from django.conf import settings

# A list of apps which don't place their media under media/app_label, placing
# it instead directly under media/
MEDIA_UTILS_PREPEND_LABEL_APPS = set(getattr(settings,
                                             'MEDIA_UTILS_PREPEND_LABEL_APPS',
                                             ('django.contrib.admin',)))

# A list of apps whose media should not be handled by media_utils
MEDIA_UTILS_SKIP_APPS = set(getattr(settings,
                                    'MEDIA_UTILS_SKIP_APPS',
                                    ()))
