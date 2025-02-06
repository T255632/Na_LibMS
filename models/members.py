# app/models/members.py
from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship
from . import db
import datetime

class Member(db.Model):
    __tablename__ = 'members'

    member_id = Column(Integer, primary_key=True)
    membership_number = Column(String(50), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    address = Column(JSON)
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    enrolled_on = Column(TIMESTAMP, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    status = Column(String(20))
    borrowing_behavior = Column(JSON)

    lending_transactions = relationship("LendingTransaction", back_populates="member")

    __table_args__ = (
        CheckConstraint("status IN ('active', 'suspended', 'deactivated')", name='check_status_valid'),
    )