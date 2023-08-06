from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

from repoze.bfg.configuration import Configurator
from repoze.bfg.wsgi import wsgiapp2
from repoze.bfg.settings import get_settings

DBSession = scoped_session(sessionmaker(autoflush=True))
Base = declarative_base()

def initialize_sql(db_string):
    engine = create_engine(db_string)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.reflect()

def make_dbbrowser_app(global_config, **settings):
    zcml_file = settings.get('configure_zcml', 'configure.zcml')
    db_string = settings.get('db_string')
    if db_string is None:
        raise ValueError("No 'db_string' in application configuration.")
    initialize_sql(db_string)
    config = Configurator(settings=settings)
    config.begin()
    config.load_zcml(zcml_file)
    config.end()
    app = config.make_wsgi_app()
    return app

@wsgiapp2
def app_view(environ, start_response):
    app = make_dbbrowser_app({},**get_settings())
    return app(environ, start_response)
