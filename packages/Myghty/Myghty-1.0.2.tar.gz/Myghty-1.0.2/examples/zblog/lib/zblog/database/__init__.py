"""global database stuff.  includes functions for finding out about database drivers, as well as the global SQLEngine used by the application."""
import zblog
import sqlalchemy.engine
import sys

def dbtypes():
    """returns a listing of SQLEngine descriptors for usage in bootstrap system"""
    return sqlalchemy.engine.engine_descriptors()
    
def get_descriptor(name):
    """returns the named SQLEngine descriptor for usage in bootstrap system."""
    for desc in dbtypes():
        if desc['name'] == name:
            break
    else:
        desc = None
    return desc
    
def test_connection(name, kwargs):
    """given a SQLEngine name and keyword arguments, creates a connection, or 
    propigates whatever exceptions occur."""
    e = sqlalchemy.engine.create_engine(name, kwargs)
    e.connection()

def init_engine():
    global engine
    conf = zblog.config['database'].copy()
    driver = conf.pop('driver')
    engine = sqlalchemy.engine.create_engine(driver, conf, echo=conf.pop('echo', False))
    # load mapper module to intialize mapper attributes on domain classes
    __import__('zblog.database.mappers')
    
# add init_engine to startup callables
zblog.startup.append(init_engine)

def init_database(admin_username, admin_password, logger):
    """creates database tables and inserts administrative user upon installation."""
    import zblog.database.tables
    if zblog.database.tables.db != engine:
        reload(zblog.database.tables)
    e = engine.echo        
    engine.echo=True
    engine.logger=logger
    zblog.database.tables.create_tables()
    import zblog.domain.user as user
    import zblog.database.mappers as mapper
    mapper.begin()
    try:
        u = user.User(admin_username, 'Administrator', admin_password, user.administrator)
        mapper.commit()
    finally:
        engine.echo = e
        engine.logger = sys.stdout