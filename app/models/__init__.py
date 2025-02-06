# app/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .staff import Staff
from .genres import Genre
from .library_resources import LibraryResource
from .borrowing_rules import BorrowingRule
from .members import Member
from .lending_transactions import LendingTransaction
from .user_roles import UserRole
from .password_policies import PasswordPolicy


def init_db(app):
    if not hasattr(app, 'extensions'):
        db.init_app(app)
    with app.app_context():
        db.create_all()