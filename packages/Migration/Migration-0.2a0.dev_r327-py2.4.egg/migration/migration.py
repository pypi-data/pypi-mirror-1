import logging

import os

from pkg_resources import resource_filename

from schema_generator import create_schema

sqlobject_available = False
try:
    import sqlobject
    import sqlobject_migration
    sqlobject_available = True
except ImportError:
    pass

sqlalchemy_available = False
try:
    import sqlalchemy
    import sqlalchemy_migration
    sqlalchemy_available = True
except ImportError:
    pass


schema_template = """from sqlalchemy import *
from sqlalchemy.databases.mysql import *

version = %i

metadata = DynamicMetaData()

"""

migration_template = """from migration.sqlalchemy_migration import *    # leave this first
from sqlalchemy import *
from %(package)s.versions.schema_%(version)i import *

# a var name metadata is imported from the schema, use it for your table
# declarations

#contacts = Table('contact_types', metadata,
#   Column('id', Integer, primary_key=True),
#   Column('name', Unicode(50), unique=True),
#)

def upgrade():
    # contacts.create()
    pass

def downgrade():
    # contacts.drop()
    pass
"""

def commit_migration(source_file, package):
    test_migration(source_file, package)
    
    print 'Commiting file into repository'
    f = open(source_file, 'r')
    source = f.read()
    f.close()
    
    new_version = get_lastest_version(package) + 1
    
    file = resource_filename(package + '.versions', 'migration_%i.py' % 
                             new_version)
    f = open(file, 'w')
    f.write(source)
    f.close()
    
    print 'New migration version %i added!' % new_version
    return
    
def test_migration(file, package):
    script = __import__(file[:-3])
    print 'Testing', file
    try:
        print 'Upgrading...',
        script.metadata.connect(get_dburi(package))
        script.upgrade()
        print 'ok!'
        print 'Downgrading...',
        script.downgrade()
        print 'ok!'
    except:
        print 'ERROR!'
        raise
    return
    
def new_migration(file, package):
    version = get_lastest_version(package)
    f = open(file, 'w')
    f.write(migration_template % dict(package=package, version=version))
    f.close()
    return

def write_schema(version, package):
    file = resource_filename(package + '.versions', 'schema_%i.py' % version)
    script = get_version_script(version, package)
    # if os.path.isfile(file):
        ## we dont overwrite existing schemas
        # print 'won\'t overwrite the schema %i' % version
        # return
    f = open(file, 'w')
    f.write(schema_template % version)
    for k,v in script.metadata.tables.iteritems():
        for row in create_schema(v):
            f.write(row + '\n')
        f.write('\n')
    f.close()
    return

def upgrade(target_version, package):
    current = get_version(package)
    dburi = get_dburi(package)
    if target_version == -1: # lastest
        target_version = get_lastest_version(package)
        
    for version in range(current + 1, target_version + 1):
        print 'upgrading', version
        script = get_version_script(version, package)
        script.metadata.connect(dburi)
        script.upgrade()
        set_version(version, package)
        write_schema(version, package)

def downgrade(target_version, package):
    current = get_version(package)
    dburi = get_dburi(package)
    for version in reversed(range(target_version + 1, current + 1)):
        print 'downgrading', version
        script = get_version_script(version, package)
        script.metadata.connect(dburi)
        script.downgrade()
        set_version(version - 1, package)

def get_orm(package):
    module = my_import(package)
    file = resource_filename(package, 'migrate.cfg')
    file = open(file, 'r')
    exec(file.read())
    file.close()
    return orm

def get_dburi(package):
    module = my_import(package)
    file = resource_filename(package, 'migrate.cfg')
    file = open(file, 'r')
    exec(file.read())
    file.close()
    return dburi

def my_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def get_lastest_version(package):
    version = 0
    while True:
        migration_file = 'migration_%i.py' % (version + 1)
        file = resource_filename(package + '.versions', migration_file)
        if not os.path.isfile(file):
            break
        version += 1
    return version

def get_version_script(version, package):
    return my_import(package + '.versions.migration_' + str(version))

def get_version(package):
    pv = _get_pv_class(package)
    return pv.get_version()

def set_version(version, package):
    pv = _get_pv_class(package)
    return pv.set_version(version)

def _get_pv_class(package):
    # if sqlobject_available:
        # pv = sqlobject_migration.get_pv_class(package)
        # if pv: return pv
    if sqlalchemy_available:
        pv = sqlalchemy_migration.get_pv_class(package)
        if pv: return pv
    return None

