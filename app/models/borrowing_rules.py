# app/models/borrowing_rules.py
from sqlalchemy import Column, Integer, String, JSON, CheckConstraint
from . import db

class BorrowingRule(db.Model):
    __tablename__ = 'borrowing_rules'

    rule_id = Column(Integer, primary_key=True)
    resource_type = Column(String(50))
    max_borrow_duration = Column(Integer)
    reminder_intervals = Column(JSON)

    __table_args__ = (
        CheckConstraint("resource_type IN ('book', 'newspaper', 'article')", name='check_resource_type_valid'),
        CheckConstraint('max_borrow_duration > 0', name='check_max_borrow_duration_positive'),
    )