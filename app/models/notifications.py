from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from . import db
import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    message = Column(String(255), nullable=False)
    # Foreign key for either member or staff (flexible for both)
    member_id = Column(Integer, ForeignKey('members.member_id', ondelete='CASCADE'), nullable=True)
    staff_id = Column(Integer, ForeignKey('staff.staff_id', ondelete='CASCADE'), nullable=True)
    role = Column(String(50), nullable=False)  # E.g., admin, staff, member
    seen = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # Define relationships for both Staff and Member
    member = relationship("Member", back_populates="notifications")
    staff = relationship("Staff", back_populates="notifications")

    __table_args__ = (
        CheckConstraint("role IN ('Admin', 'Staff', 'Member')", name='check_role_valid'),
    )
