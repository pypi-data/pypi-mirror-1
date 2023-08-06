from django.core.management.base import NoArgsCommand
from django.conf import settings
from optparse import make_option
  
class Command(NoArgsCommand):
    help = "Migrate database schema."
    requires_model_validation = False
    
    option_list = NoArgsCommand.option_list + (
        make_option('--verify', action='store_true', dest='verify', default=False, help='Verify patches'),
        make_option('--test', action='store_true', dest='test', default=False, help='Test patches'),
    )
    
    def handle_noargs(self, **options):
        try:
            from pgmigrate import DbPatcher, DbPatchFile
        except ImportError:
            print "To use \"migrate\" command install \"pgmigrate\" package, by executing \"easy_install pgmigrate\""
            return

        if settings.DATABASE_ENGINE != 'postgresql_psycopg2':
            print 'PgMigrate so far works only with Psycopg2. Sorry :/'
            return
        
        p = DbPatcher(settings.DATABASE_NAME, settings.DATABASE_HOST, settings.DATABASE_PORT, settings.DATABASE_USER, settings.DATABASE_PASSWORD, True)

        try:
            dbpatch_path = settings.DATABASE_PATCH_FILE
        except AttributeError:
            print "Please specify path to your patch file as DATABASE_PATCH_FILE in your settings file"
            return
            
        f = DbPatchFile(dbpatch_path)
        p.set_patch_file(f)
        
        if options['verify']:
            p.verify()
        elif options['test']:
            p.test()
        else:
            p.patch()
