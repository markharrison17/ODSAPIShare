"""Contact class"""

import sys

import os.path
from sqlalchemy import Column, Integer, String
from models.base import Base

# setup path so we can import our own models and controllers
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class Contact(Base):
    """
    Contacts class that keeps track of information about a
    particular Contacts. This class uses SQLAlchemy as an ORM

    """
    __tablename__ = 'contacts'

    ref = Column(Integer, primary_key=True)
    org_odscode = Column(String(10), index=True)
    type = Column(String(12), index=True)
    value = Column(String(255))


    # Returns a printable version of the objects contents
    def __repr__(self):
        return "<Contact('%s %s %s %s')>" % (
            self.ref,
            self.org_odscode,
            self.type,
            self.value)
