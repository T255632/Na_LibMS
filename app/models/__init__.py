from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

from .staff import Staff
from .genres import Genre
from .library_resources import LibraryResource
from .borrowing_rules import BorrowingRule
from .members import Member
from .lending_transactions import LendingTransaction
from .user_roles import UserRole
from .password_policies import PasswordPolicy
from .notifications import Notification


def init_db(app):
    if not hasattr(app, 'extensions'):
        db.init_app(app)
    with app.app_context():
        print("Initializing Database...")

        try:
            db.create_all()
            print("Tables created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")
            db.session.rollback()

        # Create the library_reports view
        view_sql = """
        CREATE OR REPLACE VIEW library_reports AS
        SELECT
            (SELECT COUNT(*) FROM library_resources) AS total_resources,
            (SELECT COUNT(*) FROM members) AS total_members,
            (SELECT COUNT(*) FROM lending_transactions WHERE return_date IS NULL) AS total_borrowed_resources,
            (SELECT COUNT(*) FROM lending_transactions WHERE return_date IS NULL AND due_date < CURRENT_DATE) AS overdue_transactions,
            (SELECT COUNT(DISTINCT genre_id) FROM library_resources WHERE genre_id IS NOT NULL) AS total_genres,
            (SELECT COUNT(*) FROM lending_transactions WHERE return_date IS NULL AND due_date < CURRENT_DATE) AS overdue_returns,
            (SELECT AVG(borrowed_count) FROM (SELECT COUNT(*) AS borrowed_count FROM lending_transactions GROUP BY member_id) AS subquery) AS avg_borrowed_per_member;
        """
        try:
            print("Creating 'library_reports' view...")
            db.session.execute(text("DROP VIEW IF EXISTS library_reports CASCADE;"))
            db.session.execute(text(view_sql))
            db.session.commit()
            print("View 'library_reports' created successfully.")
        except Exception as e:
            print(f"Error creating view: {e}")
            db.session.rollback()

        # Ensure default admin user exists
        print("Checking for existing default admin user...")
        default_admin = Staff.query.filter_by(name='Administrator').first()

        if not default_admin:
            print("Default admin user not found. Creating...")

            try:
                # Create the admin staff record
                admin_staff = Staff(
                    name='Administrator',
                    qualification='N/A',
                    experience='N/A',
                    skill_set='Management',
                    grade='A',
                    contact_info='admin@nalib.com',
                    role='Admin',
                    status=True
                )
                db.session.add(admin_staff)
                db.session.commit()
                print(f"Admin staff created with staff_id: {admin_staff.staff_id}")

                # Add the admin user role with hashed password
                admin_role = UserRole(
                    staff_id=admin_staff.staff_id,
                    role='Admin',
                    password_hash=generate_password_hash('admin123')  # Default password
                )
                db.session.add(admin_role)
                db.session.commit()
                print("Default admin user created successfully with default password 'nalib@2025'.")

            except Exception as e:
                print(f"Error creating default admin user: {e}")
                db.session.rollback()
        else:
            print("Default admin user already exists.")
