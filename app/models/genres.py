# app/models/genres.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from . import db

class Genre(db.Model):
    __tablename__ = 'genres'

    genre_id = Column(Integer, primary_key=True)
    genre_name = Column(String(100), nullable=False, unique=True)

    library_resources = relationship("LibraryResource", back_populates="genre")