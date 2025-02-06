# app/models/password_policies.py
from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, Interval
from sqlalchemy.orm import relationship
from . import db
import datetime

class PasswordPolicy(db.Model):
    __tablename__ = 'password_policies'

    policy_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_roles.user_id'), unique=True)
    last_changed = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    expires_after = Column(Interval, default=datetime.timedelta(days=90))

    user_role = relationship("UserRole", back_populates="password_policy")