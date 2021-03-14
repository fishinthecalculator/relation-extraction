from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .model import Base


def setup_db(path):
    # sqlite://<nohostname>/<path>
    # where <path> is relative:
    engine = create_engine(f"sqlite:///{path}/tweets.db")
    session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine))
    Base.metadata.create_all(bind=engine)
    return engine, session


def tear_down(session):
    session.close()
