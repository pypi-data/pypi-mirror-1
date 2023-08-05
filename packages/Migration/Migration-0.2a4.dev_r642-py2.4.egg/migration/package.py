def get_migrations_module(package):
    #migrations = getattr(__import__(package, {}, {}, ["migrations"]), "migrations", None)
    migrations = __import__(package, {}, {})
    return migrations
    
