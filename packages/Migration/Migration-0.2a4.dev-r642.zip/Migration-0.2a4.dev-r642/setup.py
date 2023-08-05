from setuptools import setup, find_packages

setup(
    name="Migration",
    version="0.2a4",
    description="A database/model migration extension for TurboGears",
    long_description="""Provides database structure versioning to TurboGears 
applications via SQLAlchemy.
Works but still on it's early stages.
If you really want to use it, send me an email.""",
    author="Claudio Martinez",
    author_email="claudio.s.martinez@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
    ],
    install_requires = ["Migrate == 0.2.2", 'SQLAlchemy == 0.3.4'],
    entry_points="""
        [turbogears.command]
        migrate = migration.migrate_command:MigrateCommand
    """
    )
    
