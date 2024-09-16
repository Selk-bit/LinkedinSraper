# models.py
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class LinkedInCompany(Base):
    __tablename__ = 'linked_in_companies'

    id = Column(Integer, primary_key=True)
    raison_social = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Define the relationship to LinkedInJob
    jobs = relationship('LinkedInJob')


class LinkedInJob(Base):
    __tablename__ = 'linked_in_jobs'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    location = Column(String)
    age = Column(String)
    url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign key to LinkedInCompany
    company_id = Column(Integer, ForeignKey('linked_in_companies.id', ondelete='SET NULL'), nullable=True)

    # Define the relationship to LinkedInCompany
    company = relationship('LinkedInCompany', back_populates='jobs')
