# app/models/library_resources.py
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from . import db
import datetime

class LibraryResource(db.Model):
    __tablename__ = 'library_resources'

    resource_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255))
    genre_id = Column(Integer, ForeignKey('genres.genre_id'))
    resource_type = Column(String(50))
    format = Column(String(50))
    available = Column(Boolean, default=True)
    location = Column(String(255))
    added_by_staff_id = Column(Integer, ForeignKey('staff.staff_id'))
    added_on = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc))

    genre = relationship("Genre", back_populates="library_resources")
    staff = relationship("Staff", back_populates="library_resources")
    lending_transactions = relationship("LendingTransaction", back_populates="library_resource")

    __table_args__ = (
        CheckConstraint("resource_type IN ('book', 'newspaper', 'article')", name='check_resource_type_valid'),
        CheckConstraint("format IN ('hardcopy', 'electronic')", name='check_format_valid'),
    )
