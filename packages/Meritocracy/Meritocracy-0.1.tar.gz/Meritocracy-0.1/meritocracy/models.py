from sqlalchemy import orm, Column
from sqlalchemy.types import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relation

# Broken import,  Have to figure out the story with this.
from meritocracy import meta

Base = declarative_base(metadata=meta.metadata)

def init_model(engine):
    """Required to set up the models"""
    sm = orm.sessionmaker(autoflush=True, autocommit=True, bind=engine)
    meta.engine = engine
    meta.Session = orm.scoped_session(sm)

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    path = Column(String(500), unique=True, nullable=False)
    current_revision = Column(String(40), nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    # Assumed to be openid or site unique account
    username = Column(String(500), unique=True)

class UserEmail(Base):
    __tablename__ = "useremails"
    user_id = Column(Integer, ForeignKey('users.id'))
    email = Column(String(500), primary_key=True)

class Contribution(Base):
    __tablename__ = "contributions"
    id = Column(Integer, primary_key=True)
    revision = Column(String(40), nullable=False)
    repo_id = Column(Integer, ForeignKey('repositories.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

