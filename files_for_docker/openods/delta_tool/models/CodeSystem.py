"""CodeSystem class"""

import sys

import os.path
from sqlalchemy import Column, Integer, String
from models.base import Base

# setup path so we can import our own models and controllers
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class CodeSystem(Base):
    """
    CodeSystems class that keeps track of information about a
    particular ods file update. This class uses SQLAlchemy as an ORM

    """
    __tablename__ = 'codesystems'

    ref = Column(Integer, primary_key=True)
    id = Column(String(10), index=True)
    name = Column(String(50))
    displayname = Column(String(200))

    # Returns a printable version of the objects contents
    def __repr__(self):
        return "<CodeSystem('%s %s %s %s'\
            )>" % (
                self.ref,
                self.name,
                self.id,
                self.displayname)
