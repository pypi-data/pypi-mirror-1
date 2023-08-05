migrations = dict()

class MigrationMeta(type):
    def __init__(cls, name, *args, **kw):
        if name not in ['Migration', 'SOMigration', 'SAMigration'] and \
           name.startswith('Migration'):
            version = int(name[-3:])
            migrations[version] = cls
        super(MigrationMeta, cls).__init__(*args, **kw)

class Migration(object):
    __metaclass__ = MigrationMeta
    def add_column(self, *args, **kw):
        assert 0, 'This has to be overriden'
    def del_column(self, *args, **kw):
        assert 0, 'This has to be overriden'
    def create_table(self, *args, **kw):
        assert 0, 'This has to be overriden'
    def drop_table(self, *args, **kw):
        assert 0, 'This has to be overriden'
    def up(self):
        assert 0, 'This has to be overriden'
    def down(self):
        assert 0, 'This has to be overriden'
    def query(self, query):
        assert 0, 'This has to be overriden'
       
class PackageVersion(object):
    def get_version(self):
        assert 0, 'This has to be overriden'
    
    def set_version(self, version):
        assert 0, 'This has to be overriden'