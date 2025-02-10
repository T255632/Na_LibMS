from flask import Blueprint, render_template, redirect, request, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db
from models.library_resources import LibraryResource
from models.lending_transactions import LendingTransaction
from models.members import Member
from datetime import datetime
import json

# Create the Blueprint for Member Routes
members_bp = Blueprint('members', __name__, template_folder='../templates/members')

def is_member():
    jwt_data = get_jwt()
    return jwt_data.get('role') == 'Member'

@members_bp.route('/member_dashboard')
@jwt_required()
def member_dashboard():
    # Check if the user is a member (you can define a helper function similar to is_staff)
    if not is_member():
        return redirect('/')  # Redirect if not a member

    # Retrieve the full JWT payload (including additional claims)
    jwt_data = get_jwt()
    member_id = jwt_data.get('member_id')
    
    # Convert member_id to int if needed (assuming the DB column is an integer)
    try:
        member_id = int(member_id)
    except (TypeError, ValueError):
        # Handle error if conversion fails (for example, redirect or show error)
        return redirect('/')
    
    member = Member.query.filter_by(member_id=member_id).first()
    if not member:
        # Optionally, render an error template or redirect if member is not found
        return redirect('/')

    borrowed_books = LendingTransaction.query.filter_by(member_id=member_id, status='borrowed').all()


    
    # Ensure this is properly indented:
    overdue_books = LendingTransaction.query.filter(
        LendingTransaction.member_id == member_id,
        LendingTransaction.status == 'borrowed',
        LendingTransaction.due_date < datetime.now()
    ).all()

    # Render the member dashboard template with member details and dashboard data
    return render_template(
        'members/member_dashboard.html', 
        member=member,
        borrowed_books=borrowed_books,
        overdue_books=overdue_books
    )



# View all library resources
@members_bp.route('/browse_resources')
@jwt_required()
def browse_resources():
    resources = LibraryResource.query.filter(LibraryResource.available == True).all()
    return render_template('members/browse_resources.html', resources=resources)

# View borrowing history
@members_bp.route('/borrowing_history')
@jwt_required()
def borrowing_history():
    member_id = get_jwt_identity()  # Get the logged-in member's ID
    transactions = LendingTransaction.query.filter_by(member_id=member_id).all()
    return render_template('members/borrowing_history.html', transactions=transactions)


@members_bp.route('/resource/details/<int:resource_id>')
@jwt_required()
def resource_details(resource_id):
    resource = LibraryResource.query.get_or_404(resource_id)
    return render_template('members/resource_details.html', resource=resource)


# Notifications for overdue books
@members_bp.route('/notifications')
@jwt_required()
def notifications():
    member_id = get_jwt_identity()  # Get the logged-in member's ID
    # Find transactions where due date has passed but not returned
    overdue_transactions = LendingTransaction.query.filter(
        LendingTransaction.member_id == member_id,
        LendingTransaction.returned_on == None,
        LendingTransaction.due_date < datetime.now()
    ).all()

    # Add notifications for overdue books
    notifications = []
    for transaction in overdue_transactions:
        notifications.append({
            'message': f"Your borrowed book '{transaction.library_resource.title}' is overdue. Please return it as soon as possible.",
            'transaction_id': transaction.transaction_id
        })

    return render_template('members/notifications.html', notifications=notifications)

# View borrowing history details (could include return reminders)
@members_bp.route('/borrowing_history/<int:transaction_id>')
@jwt_required()
def borrowing_history_details(transaction_id):
    transaction = LendingTransaction.query.get_or_404(transaction_id)
    return render_template('members/borrowing_history_details.html', transaction=transaction)

