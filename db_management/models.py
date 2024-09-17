# models.py
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


# Abstract base model
class BaseModel(Base):
    __abstract__ = True  # Mark this as an abstract base class
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LinkedInCompany(BaseModel):
    __tablename__ = 'linked_in_companies'

    raison_social = Column(String(255), unique=True)
    # Define the relationship to LinkedInJob
    jobs = relationship('LinkedInJob')


class LinkedInJob(BaseModel):
    __tablename__ = 'linked_in_jobs'

    title = Column(String(255))
    description = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    age = Column(String(255), nullable=True)
    url = Column(String(600), unique=True)
    # Foreign key to LinkedInCompany
    company_id = Column(Integer, ForeignKey('linked_in_companies.id', ondelete='SET NULL'), nullable=True)
    # Define the relationship to LinkedInCompany
    company = relationship('LinkedInCompany', back_populates='jobs')
    transmitted = Column(Boolean, default=False)


class ScrapingJob(BaseModel):
    __tablename__ = 'scraping_jobs'
    hash = Column(String(255), unique=True)
