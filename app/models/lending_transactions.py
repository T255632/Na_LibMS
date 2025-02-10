from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from . import db
import datetime

class LendingTransaction(db.Model):
    __tablename__ = 'lending_transactions'

    transaction_id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.member_id'))
    resource_id = Column(Integer, ForeignKey('library_resources.resource_id'))
    borrowed_on = Column(TIMESTAMP, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    due_date = Column(TIMESTAMP, nullable=False)
    returned_on = Column(TIMESTAMP)
    return_date = Column(TIMESTAMP)  # New field for actual return date
    status = Column(String(20))
    condition_on_return = Column(String(20))
    staff_id = Column(Integer, ForeignKey('staff.staff_id'))
    reward_points = Column(Integer, default=0)  # New field to store reward points

    member = relationship("Member", back_populates="lending_transactions")
    library_resource = relationship("LibraryResource", back_populates="lending_transactions")
    staff = relationship("Staff", back_populates="lending_transactions")

    __table_args__ = (
        CheckConstraint("status IN ('borrowed', 'returned', 'overdue', 'damaged', 'lost')", name='check_status_valid'),
        CheckConstraint("condition_on_return IN ('good', 'damaged', 'lost')", name='check_condition_on_return_valid'),
    )

    def calculate_reward(self):
        """
        Reward points logic: 10 points if returned on or before due date.
        """
        if self.return_date and self.return_date <= self.due_date:
            self.reward_points = 10
        else:
            self.reward_points = 0
