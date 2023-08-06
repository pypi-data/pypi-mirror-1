from tempfile import mkdtemp
import shutil
import os

from django.conf import settings
from django.test import TestCase
from django.core.management import call_command

NEED_SETTINGS_MODULE = 'media_utils.tests.test_settings'
NO_VALUE = object()

class MediaUtilsTestCase(TestCase):
    def setUp(self):
        """
        Make sure we have the settings we need for these tests.
        
        """
        self._old_settings = {}
        if settings.SETTINGS_MODULE != NEED_SETTINGS_MODULE:
            settings_mod = __import__(NEED_SETTINGS_MODULE, {}, {}, [''])
            for setting in dir(settings_mod):
                self._old_settings[setting] = getattr(settings, setting,
                                                      NO_VALUE)
                setattr(settings, setting, getattr(settings_mod, setting))

    def tearDown(self):
        """
        Restore previous settings.

        """
        for k,v in self._old_settings.items():
            setattr(settings, k, v)

class TestLinkMediaCommand(MediaUtilsTestCase):
    def setUp(self):
        super(TestLinkMediaCommand, self).setUp()
        self.tmp_dir = mkdtemp()
        call_command('link_media', self.tmp_dir, verbosity=0)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        super(TestLinkMediaCommand, self).tearDown()

    def _get_file(self, filepath):
        return open(os.path.join(self.tmp_dir, filepath)).read()

    def testClean(self):
        """
        --clean option cleans out files in destination directory prior
          to linking.

        """
        fh = open(os.path.join(self.tmp_dir, 'added'), 'w')
        fh.write('something')
        fh.close()
        call_command('link_media', self.tmp_dir, verbosity=0, clean=True)
        self.assert_(not os.path.exists(os.path.join(self.tmp_dir, 'added')))
    
    def testProjectMedia(self):
        """
        Files in project media are linked.

        """
        self.assert_('Can we find' in self._get_file('test.txt'))
            
    def testDeeperProjectMedia(self):
        """
        Files in project media subdirectories are linked.

        """
        self.assert_('Can we find' in self._get_file('subdir/test.txt'))
            
    def testProjectMediaPriority(self):
        """
        MEDIA_ROOT/appname/file.txt has priority over
        APP_DIR/media/file.txt.

        """
        self.assert_('project' in self._get_file('test_app/file.txt'))

    def testAppMedia(self):
        """
        Files are linked from app dirs (because a test_app directory
        exists in the project MEDIA_ROOT, this also tests the support
        for selective file masking).
        
        """
        self.assert_('file1 in the app dir'
                     in self._get_file('test_app/file1.txt'))

    def testNoLabelAppMedia(self):
        """
        Files are linked from the app dir of an app that doesn't put
        its media inside an app_label/ subdirectory, if that app is
        listed in MEDIA_UTILS_PREPEND_LABEL_APPS.
        
        """
        self.assert_('file2 in no_label_app'
                     in self._get_file('no_label_app/file2.txt'))

    def testSkipApp(self):
        """
        Test that media files for apps in MEDIA_UTILS_SKIP_APPS are
        not linked.
        
        """
        self.assertRaises(IOError, self._get_file, 'skip_app/skip_file.txt')
        
class TestServeAppMediaView(MediaUtilsTestCase):
    def testProjectMedia(self):
        """
        A file can be fetched from the project media directory.

        """
        r = self.client.get('/media/test.txt')
        self.assertContains(r, 'Can we find', status_code=200)

    def testDeeperProjectMedia(self):
        """
        A file can be fetched from a subdirectory of the project media
        directory.

        """
        r = self.client.get('/media/subdir/test.txt')
        self.assertContains(r, 'Can we find', status_code=200)

    def testProjectMediaPriority(self):
        """
        MEDIA_ROOT/appname/file.txt has priority over
        APP_DIR/media/file.txt.

        """
        r = self.client.get('/media/test_app/file.txt')
        self.assertContains(r, 'project', status_code=200)

    def testAppMedia(self):
        """
        A file can be served from an app dir.
        
        """
        r = self.client.get('/media/test_app/file1.txt')
        self.assertContains(r, 'file1 in the app dir', status_code=200)

    def testNoLabelAppMedia(self):
        """
        A file can be served from an app dir of an app that doesn't
        put its media inside an app_label/ subdirectory, if that app
        is listed in MEDIA_UTILS_PREPEND_LABEL_APPS.
        
        """
        r = self.client.get('/media/no_label_app/file2.txt')
        self.assertContains(r, 'file2 in no_label_app', status_code=200)
        
    def testProject404(self):
        """
        Looking for a nonexistent file in MEDIA_ROOT raises 404.
        
        """
        r = self.client.get('/media/notthere.txt')
        self.assertEquals(r.status_code, 404)

    def testApp404(self):
        """
        Looking for a nonexistent file in an app dir raises 404.
        
        """
        r = self.client.get('/media/test_app/notthere.txt')
        self.assertEquals(r.status_code, 404)

    def testSkipApp(self):
        """
        Test that media files for apps in MEDIA_UTILS_SKIP_APPS are
        not served.
        
        """
        r = self.client.get('/media/skip_app/skip_file.txt')
        self.assertEquals(r.status_code, 404)
        
