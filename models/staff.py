# app/models/staff.py
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from . import db

class Staff(db.Model):
    __tablename__ = 'staff'

    staff_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    qualification = Column(Text)
    experience = Column(Text)
    skill_set = Column(Text)
    grade = Column(String(50))
    contact_info = Column(JSON)
    role = Column(String(50))
    status = Column(Boolean, default=True)

    library_resources = relationship("LibraryResource", back_populates="staff")
    lending_transactions = relationship("LendingTransaction", back_populates="staff")
    user_role = relationship("UserRole", back_populates="staff", uselist=False)

    __table_args__ = (
        CheckConstraint("role IN ('Admin', 'Staff', 'Member')", name='check_role_valid'),
    )