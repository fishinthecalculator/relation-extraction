from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Tweet(Base):
    __tablename__ = "tweet"
    tweet_id = Column(Integer, primary_key=True)
    full_text = Column(String)
    created_at = Column(String)
    lang = Column(String)
