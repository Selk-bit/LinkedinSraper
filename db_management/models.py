# models.py

from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class LinkedInJob(Base):
    __tablename__ = 'linked_in_jobs'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    location = Column(String)
    age = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class LinkedInCompany(Base):
    __tablename__ = 'linked_in_companies'

    id = Column(Integer, primary_key=True)
    raison_social = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
