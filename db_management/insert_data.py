# insert_data.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_management.models import Base, LinkedInJob, LinkedInCompany

# Connect to the SQLite database
engine = create_engine('sqlite:///linked_in.db')

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
session = Session()
