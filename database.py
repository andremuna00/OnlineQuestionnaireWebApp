from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# DB CONNECTION SETTINGS
user = "postgres"
psw = "root"
ipAddr = "localhost"
port = "5432"
dbName = "form"
engine = create_engine('postgresql+psycopg2://'+user+':'+psw+'@'+ipAddr+':'+port+'/'+dbName, pool_size=15,
                       max_overflow=50, isolation_level='REPEATABLE READ')

Base = declarative_base()
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db() import models
    Base.metadata.create_all(bind=engine)
