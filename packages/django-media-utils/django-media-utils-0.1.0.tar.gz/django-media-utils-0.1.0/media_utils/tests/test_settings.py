import os

BASE_DIR = os.path.dirname(__file__)

INSTALLED_APPS = (
    'media_utils',
    'media_utils.tests.test_app',
    'media_utils.tests.no_label_app',
    'media_utils.tests.skip_app'
    )

MEDIA_ROOT = os.path.join(BASE_DIR, 'test_project', 'media')

ROOT_URLCONF = 'media_utils.tests.test_urls'

MEDIA_UTILS_PREPEND_LABEL_APPS = ('media_utils.tests.no_label_app',)

MEDIA_UTILS_SKIP_APPS = ('media_utils.tests.skip_app',)

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'),)

DATABASE_ENGINE = 'sqlite3'

APPEND_SLASH = False
