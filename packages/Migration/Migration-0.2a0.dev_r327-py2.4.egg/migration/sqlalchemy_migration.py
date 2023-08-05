from sqlalchemy import *
from sqlalchemy.ext.sessioncontext import SessionContext
from sqlalchemy.ext.assignmapper import assign_mapper

from package import get_migrations_module

from base_classes import Migration, PackageVersion

from pkg_resources import resource_filename

from migrate.changeset import *

from migrate import driver

metadata = DynamicMetaData()

tg_migrate = Table('tg_migrate', metadata,
    Column('id', Integer, primary_key=True),
    Column('package', String(50), unique=True),
    Column('version', Integer))

class SAPackageVersion(PackageVersion):
    def get_version(self):
        return self.version
        
    def set_version(self, version):
        self.version = version
        self.flush()

assign_mapper(SessionContext(create_session), SAPackageVersion, tg_migrate)

def my_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def get_pv_class(package):
    module = my_import(package)
    file = resource_filename(package, 'migrate.cfg')
    file = open(file, 'r')
    exec(file.read())
    file.close()
    
    if not metadata.engine:
        metadata.connect(dburi)
        tg_migrate.create(checkfirst=True)
    
    pv = SAPackageVersion.get_by(package=package)
    if not pv:
        pv = SAPackageVersion()
        pv.package = package
        pv.version = 0
        pv.save()
        pv.flush()
    
    return pv

def get_fk_constraint(col):
    from migrate.changeset.constraint import ForeignKeyConstraint
    f_key = col.foreign_key
    fkc = ForeignKeyConstraint([f_key.parent], [f_key.column])
    fkc.name = f_key.constraint.name
    return fkc

def drop_column(col, table=None):
    col = copy(col) # we dont want to change the original column, static schema
    if getattr(col, 'foreign_key'):
        constraint = get_fk_constraint(col)
        constraint.drop()
    if table:
        col.drop(table)
    else:
        col.drop()
    try:
        del(col.table.columns[col.name])
    except KeyError:
        pass
    
def add_column(col, table=None):
    col = copy(col) # we dont want to change the original column, static schema
    if table:
        col.create(table)
    else:
        col.create()
    col.table.columns[col.name] = col
    if getattr(col, 'foreign_key'):
        constraint = get_fk_constraint(col)
        constraint.create()

from copy import copy
def alter_column(old_col, new_col):
    if old_col.table:
        table = old_col.table
    else:
        table = new_col.table
    
    # we make a copy of the column because migrate changes the original column
    # which screws the overall schema as we use it
    old_col = copy(old_col)
    
    # just in case this is a downgrade and it doesnt have a table specificied
    old_col.table = table
    
    # we add the column if it doesnt exist (probably downgrading)
    table.columns[old_col.name] = old_col
    try:
        # we del the new_column if it already exists (probably downgrading)
        del(table.columns[new_col.name])
    except KeyError:
        pass
    old_name = old_col.name
    old_col.alter(new_col)
    
    # its old_col and not new_col because attrs
    # are copied (except the table I guess)
    table.columns[new_col.name] = old_col

