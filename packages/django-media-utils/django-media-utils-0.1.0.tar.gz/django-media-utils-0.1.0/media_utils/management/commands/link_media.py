"""
link_media management command

"""
import sys
import os
import shutil
from optparse import make_option

from django.core.management import BaseCommand
from django.conf import settings

from media_utils.settings import MEDIA_UTILS_PREPEND_LABEL_APPS, \
    MEDIA_UTILS_SKIP_APPS

class Command(BaseCommand):
    help = 'Symlink project and app static media files to <media-www-dir>'
    args = '<media-www-dir>'
    requires_model_validation = False
    
    option_list = BaseCommand.option_list + (
        make_option('--clean', action='store_true', default=False,
                    help='Clean <media-www-dir> before creating links'),
    )

    def handle(self, *args, **options):
        self.traceback = options.get('traceback', False)
        self.verbosity = options['verbosity']
        
        try:
            media_dir = os.path.abspath(args[0])
        except IndexError:
            self.error()
            
        if not os.path.isdir(media_dir):
            self.error("Not a directory: %s\n" % media_dir)

        if self.verbosity:
            print "Creating symlinks in %s" % media_dir
        if options['clean']:
            if self.verbosity:
                print 'Cleaning...'
            for f in os.listdir(media_dir):
                if self.verbosity > 1:
                    print '  Removing %s' % f
                path = os.path.join(media_dir, f)
                try:
                    os.remove(path)
                except OSError, e:
                    self.error('Could not clean %s: %s' % (path, e))
                    
        self.handle_directory(settings.MEDIA_ROOT, media_dir)
                    
        for app in settings.INSTALLED_APPS:
            if app in MEDIA_UTILS_SKIP_APPS:
                continue
            app_label = app.split('.')[-1]
            mod = __import__(app, {}, {}, [app_label])
            app_media_dir = os.path.join(os.path.dirname(mod.__file__), 'media')
            if os.path.isdir(app_media_dir):
                if app in MEDIA_UTILS_PREPEND_LABEL_APPS:
                    self.symlink(app_media_dir, os.path.join(media_dir,
                                                             app_label))
                else:
                    self.handle_directory(app_media_dir, media_dir)

    def handle_directory(self, d, dest_dir):
        d = os.path.normpath(d)
        if self.verbosity:
            print "Symlinking files in %s" % d
        for f in os.listdir(d):
            src = os.path.join(d, f)
            dst = os.path.join(dest_dir, f)
            self.symlink(src, dst)
            
    def symlink(self, src, dst):
        try:
            os.symlink(src, dst)
            if self.verbosity > 1:
                print "  Linked %s" % src
        except OSError, e:
            # if this is a directory already linked elsewhere, recurse
            # into it (to handle selective masking of files in app dir
            # by project dir)
            if (e.errno == os.errno.EEXIST and
                os.path.islink(dst) and
                os.path.isdir(dst) and
                not os.path.samefile(src, dst)):
                self.handle_directory(src, dst)
            if self.verbosity:
                print "  Could not link %s: %s" % (src, e)
            pass
            
    def error(self, message=None):
        if message is not None:
            print
            print message
        self.print_help(sys.argv[0], sys.argv[1])
        if self.traceback and sys.exc_info()[0] is not None:
            raise
        sys.exit(1)
        
    
