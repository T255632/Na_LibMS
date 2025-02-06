# app/models/user_roles.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from . import db

class UserRole(db.Model):
    __tablename__ = 'user_roles'

    user_id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey('staff.staff_id'), unique=True)
    role = Column(String(50), CheckConstraint("role IN ('Admin', 'Staff', 'Member')"))
    password_hash = Column(Text, nullable=False)

    staff = relationship("Staff", back_populates="user_role", uselist=False)
    password_policy = relationship("PasswordPolicy", back_populates="user_role", uselist=False)