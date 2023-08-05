import sys
import migration
import turbogears

from turbogears.command.base import CommandWithDB
from optparse import OptionParser

class MigrateCommand(CommandWithDB):
    """Database migration tool"""

    desc = "Database migration tool"

    def __init__(self, *args, **kwargs):
        pass
        
    def run(self):
        usage = "%prog migrate option"
        parser = OptionParser()
        parser.add_option('-p', '--package', 
                          action='store', type='string', dest='package')
        parser.add_option('-c', '--config', 
                          action='store', type='string', dest='config')
                          
        (options, args) = parser.parse_args()
        if not options.package:
            print 'You need to specify the repository package name with ' \
                  'tg-admin migrate -p your_app.migrate command'
            sys.exit()
        
        #load_conf(config=options.config, package=options.package)
        self.package = options.package
        
        if args[0] == 'upgrade':
            version = -1 # -1 means the lastest
            if len(args) > 2:
                version = int(args[1])
            self.upgrade(version)
        elif args[0] == 'downgrade':
            if len(args) < 2:
                print 'usage: tg-admin migrate downgrade version_number'
                return
            version = int(args[1])
            self.downgrade(version)
        elif args[0] == 'version':
            self.get_version()
        elif args[0] == 'set_version':
            version = int(args[1])
            self.set_version(version)
        elif args[0] == 'new_migration':
            if len(args) < 2:
                print 'usage: tg-admin migrate new_migration file_name.py'
                return
            self.new_migration(args[1])
        elif args[0] == 'test_migration':
            if len(args) < 2:
                print 'usage: tg-admin migrate test_migration file_name.py'
                return
            self.test_migration(args[1])
        elif args[0] == 'commit_migration':
            if len(args) < 2:
                print 'usage: tg-admin migrate commit_migration file_name.py'
                return
            self.commit_migration(args[1])
        else: 
            print usage
    
    def new_migration(self, file):
        migration.new_migration(file=file, package=self.package)
    
    def test_migration(self, file):
        migration.test_migration(file=file, package=self.package)
    
    def commit_migration(self, file):
        migration.commit_migration(source_file=file, package=self.package)
    
    def upgrade(self, version):
        if version == -1:
            print 'Migrating database to lastest version'
        else:
            print 'Migrating database to version %s' % version
        migration.upgrade(target_version=version, package=self.package)
        
    def downgrade(self, version):
        print 'Downgrading database to version %s' % version
        migration.downgrade(target_version=version, package=self.package)
    
    def set_version(self, version):
        version = int(version)
        print 'Setting database to version %s (no migration will be done)' % \
               version
        migration.set_version(version=version, package=self.package)
        
    def get_version(self):
        print 'The current database version is %s' % \
               migration.get_version(package=self.package)
        print 'The lastest database version is %s' % \
               migration.get_lastest_version(package=self.package)
