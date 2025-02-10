from flask import Blueprint, render_template, redirect, request, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db
from models.staff import Staff
from models.library_resources import LibraryResource
from models.genres import Genre
from models.borrowing_rules import BorrowingRule
from models.lending_transactions import LendingTransaction
from models.members import Member
import json
import logging
from datetime import datetime, timedelta

# Create the Blueprint for Staff Routes
staff_bp = Blueprint('staff', __name__, template_folder='../templates/staff')

def is_staff():
    jwt_data = get_jwt()
    return jwt_data.get('role') == 'Staff'


@staff_bp.route('/dashboard')
@jwt_required()
def staff_dashboard():
    if not is_staff():
        return redirect('/')  # Redirect if not staff

    # Retrieve the full JWT payload (including additional claims)
    jwt_data = get_jwt()
    staff_id = jwt_data.get('staff_id')
    
    # Convert staff_id to int if needed (assuming the DB column is an integer)
    try:
        staff_id = int(staff_id)
    except (TypeError, ValueError):
        # Handle error if conversion fails (for example, redirect or show error)
        return redirect('/')
    
    staff_member = Staff.query.filter_by(staff_id=staff_id).first()
    if not staff_member:
        # Optionally, render an error template or redirect if staff_member is not found
        return redirect('/')

    # Gather dashboard data for staff
    total_resources = LibraryResource.query.count()
    total_members = Member.query.count()
    total_borrowed_resources = LendingTransaction.query.filter(LendingTransaction.status == 'borrowed').count()

    # Render the staff dashboard template with the staff details and dashboard data
    return render_template(
        'staff/dashboard.html', 
        staff_member=staff_member,
        total_resources=total_resources,
        total_members=total_members,
        total_borrowed_resources=total_borrowed_resources
    )




@staff_bp.route('/profile')
@jwt_required()
def profile():
    staff_member = get_current_user()

    # Convert contact_info from JSON string to dictionary
    if isinstance(staff_member.contact_info, str):
        try:
            staff_member.contact_info = json.loads(staff_member.contact_info)
        except json.JSONDecodeError:
            staff_member.contact_info = {}  # Handle invalid JSON

    return render_template('staff/profile.html', staff_member=staff_member)

@staff_bp.route('/edit_profile', methods=['GET', 'POST'])
@jwt_required()
def edit_profile():
    if not is_staff():
        return redirect('/')  # Redirect if not staff

    jwt_data = get_jwt()
    staff_id = jwt_data.get('staff_id')

    try:
        staff_id = int(staff_id)
    except (TypeError, ValueError):
        return redirect('/')  # Redirect if invalid ID

    staff_member = Staff.query.get(staff_id)
    if not staff_member:
        return redirect('/')  # Redirect if staff not found

    if request.method == 'POST':
        # Basic validation (optional but recommended)
        staff_member.name = request.form.get('name', staff_member.name)
        staff_member.qualification = request.form.get('qualification', staff_member.qualification)
        staff_member.experience = request.form.get('experience', staff_member.experience)
        staff_member.skill_set = request.form.get('skill_set', staff_member.skill_set)
        staff_member.grade = request.form.get('grade', staff_member.grade)
        
        # Safely parse contact_info if it's JSON formatted
        contact_info = request.form.get('contact_info')
        try:
            staff_member.contact_info = json.dumps(json.loads(contact_info)) if contact_info else staff_member.contact_info
        except json.JSONDecodeError:
            staff_member.contact_info = staff_member.contact_info  # Keep previous value if invalid

        # Handling status as checkbox (adjust if needed)
        staff_member.status = request.form.get('status') == 'true'

        db.session.commit()
        return redirect(url_for('staff.profile'))

    return render_template('staff/edit_profile.html', staff_member=staff_member)


# Utility function to get the current staff user
def get_current_user():
    jwt_data = get_jwt()  # Use get_jwt() to access JWT claims
    staff_id = jwt_data.get('staff_id')

    try:
        staff_id = int(staff_id)
    except (TypeError, ValueError):
        return None  # Return None if invalid staff_id

    return Staff.query.get(staff_id)




# Resource Management Routes
@staff_bp.route('/manage_resources', methods=['GET'])
@jwt_required()
def manage_resources():
    if not is_staff():
        return redirect('/')  # Redirect to home or unauthorized page
    
    resources = LibraryResource.query.all()
    return render_template('staff/resources_management.html', resources=resources)


@staff_bp.route('/add_resource', methods=['GET', 'POST'])
@jwt_required()
def add_resource():
    if not is_staff():
        return redirect('/')  # Redirect to home or unauthorized page

    staff_member = get_current_user()
    if not staff_member:
        return redirect('/')  # Redirect if staff not found

    genres = Genre.query.all()  # Fetch all genres for dropdown

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre_id = request.form.get('genre_id')
        resource_type = request.form.get('resource_type')
        format = request.form.get('format')
        location = request.form.get('location')

        try:
            items = int(request.form.get('items', 0))
            if items < 0:
                return "Items cannot be negative", 400
        except ValueError:
            return "Invalid number of items", 400

        new_resource = LibraryResource(
            title=title,
            author=author,
            genre_id=genre_id,
            resource_type=resource_type,
            format=format,
            location=location,
            items=items,
            added_by_staff_id=staff_member.staff_id,
            available=True  # Default available status
        )

        db.session.add(new_resource)
        db.session.commit()
        return redirect(url_for('staff.manage_resources'))  # Redirect to resource management page

    return render_template('staff/add_resource.html', genres=genres)


# Helper function to get genre_id by genre name
def get_genre_id_by_name(genre_name):
    genre = Genre.query.filter_by(genre_name=genre_name).first()
    if not genre:
        raise ValueError(f"Genre '{genre_name}' not found.")
    return genre.genre_id


@staff_bp.route('/edit_resource/<int:resource_id>', methods=['GET', 'POST'])
@jwt_required()
def edit_resource(resource_id):
    if not is_staff():
        return redirect('/')  # Redirect to home or unauthorized page

    staff_member = get_current_user()
    if not staff_member:
        return redirect('/')  # Redirect if staff not found

    resource = LibraryResource.query.get_or_404(resource_id)
    genres = Genre.query.all()  # Fetch all genres for dropdown

    if request.method == 'POST':
        resource.title = request.form.get('title')
        resource.author = request.form.get('author')

        # Using helper function to get genre_id
        genre_name = request.form.get('genre_name')
        try:
            genre_id = get_genre_id_by_name(genre_name)
        except ValueError:
            return "Genre not found", 400  # Handle invalid genre

        resource.genre_id = genre_id
        resource.resource_type = request.form.get('resource_type')
        resource.format = request.form.get('format')
        resource.location = request.form.get('location')

        try:
            items = int(request.form.get('items', 0))
            if items < 0:
                return "Items cannot be negative", 400
        except ValueError:
            return "Invalid number of items", 400

        resource.items = items

        db.session.commit()
        return redirect(url_for('staff.manage_resources'))  # Redirect to resource management page

    return render_template('staff/edit_resource.html', resource=resource, genres=genres)




# Utility function to get the current staff user
def get_current_user():
    jwt_data = get_jwt()
    staff_id = jwt_data.get('staff_id')

    try:
        staff_id = int(staff_id)
    except (TypeError, ValueError):
        return None

    return Staff.query.get(staff_id)


# Lending Transactions Management Route
@staff_bp.route('/manage_lending_transactions')
@jwt_required()
def manage_lending_transactions():
    if not is_staff():
        return redirect('/')

    lending_transactions = LendingTransaction.query.all()
    return render_template('staff/create_lending_transactions.html', lending_transactions=lending_transactions)

@staff_bp.route('/create_lending_transaction', methods=['GET', 'POST'])
@jwt_required()
def add_lending_transaction(): 
    if not is_staff():
        return redirect('/')

    staff_member = get_current_user()
    if not staff_member:
        return redirect('/')

    if request.method == 'POST':
        try:
            member_id = int(request.form.get('member_id'))
            resource_id = int(request.form.get('resource_id'))
        except (ValueError, TypeError):
            return "Invalid member or resource ID", 400

        member = Member.query.get(member_id)
        resource = LibraryResource.query.get(resource_id)

        if not member:
            return "Member not found", 404
        if not resource:
            return "Resource not found", 404

        # Borrowing limit check
        borrowing_limit = 5
        current_borrowed = LendingTransaction.query.filter_by(member_id=member_id, status='borrowed').count()
        if current_borrowed >= borrowing_limit:
            return "Member has reached the borrowing limit.", 400

        borrowing_rule = BorrowingRule.query.filter_by(resource_type=resource.resource_type).first()
        if not borrowing_rule:
            return "Borrowing rule not found for this resource type", 404

        # Handle due date
        due_date_form = request.form.get('due_date')
        if due_date_form:
            try:
                due_date = datetime.strptime(due_date_form, '%Y-%m-%d')
            except ValueError:
                return "Invalid due date format", 400
        else:
            due_date = datetime.now() + timedelta(days=borrowing_rule.max_borrow_duration)

        if resource.items <= 0 or not resource.available:
            return "Resource is currently unavailable", 400

        new_transaction = LendingTransaction(
            member_id=member_id,
            resource_id=resource_id,
            due_date=due_date,
            status='borrowed',
            staff_id=staff_member.staff_id
        )

        # Transaction safety
        try:
            resource.items -= 1
            resource.available = resource.items > 0

            db.session.add(new_transaction)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"An error occurred: {str(e)}", 500

        return redirect(url_for('staff.manage_lending_transactions'))

    members = Member.query.all()
    resources = LibraryResource.query.filter(LibraryResource.available == True).all()
    return render_template('staff/create_lending_transactions.html', members=members, resources=resources)




def mark_book_as_returned(transaction_id):
    """Mark the book as returned and update the transaction."""
    logging.debug(f"Attempting to mark book as returned for transaction_id: {transaction_id}")
    
    # Retrieve the transaction
    transaction = LendingTransaction.query.filter_by(transaction_id=transaction_id, returned_on=None).first()

    if transaction:
        logging.debug(f"Transaction found: {transaction.transaction_id} for resource {transaction.resource_id}")
        
        # Mark the transaction as returned
        transaction.returned_on = datetime.utcnow()
        transaction.status = 'returned'
        
        # Retrieve the associated resource
        resource = LibraryResource.query.get(transaction.resource_id)
        if resource:
            logging.debug(f"Resource found: {resource.resource_id}, current available items: {resource.items}")
            
            # Increment the resource's available items count
            resource.items += 1
            resource.available = True  # Ensure the resource is marked as available
            logging.debug(f"Resource items updated: {resource.items}, resource available set to: {resource.available}")

            # Commit the changes to the database
            db.session.commit()
            logging.debug("Transaction and resource updates committed to the database.")
            return True
        else:
            logging.warning(f"Resource with ID {transaction.resource_id} not found.")
    else:
        logging.warning(f"Transaction with ID {transaction_id} not found or already returned.")
    
    return False



@staff_bp.route('/receive_book', methods=['GET', 'POST'])
def receive_book():
    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')

        # Validate the transaction and mark the book as returned
        if mark_book_as_returned(transaction_id):
            alert_message = 'Invalid transaction ID or book already returned.'
        else:
            alert_message = 'This book has already been returned.'

        return redirect(url_for('staff.receive_book'))  # Redirect to the same page after submission

    # Only show books that are not yet returned
    transactions = LendingTransaction.query.filter_by(returned_on=None).all()
    return render_template('staff/create_lending_transactions.html', transactions=transactions)



@staff_bp.route('/manage_genres', methods=['GET'])
@jwt_required()
def manage_genres():
    if not is_staff():
        return redirect('/')  # Redirect to home or unauthorized page
    
    genres = Genre.query.all()
    return render_template('staff/manage_genres.html', genres=genres)


@staff_bp.route('/add_genre', methods=['GET', 'POST'])
@jwt_required()
def add_genre():
    if not is_staff():
        return redirect('/')  # Redirect to home or unauthorized page

    if request.method == 'POST':
        genre_name = request.form['genre_name']
        new_genre = Genre(genre_name=genre_name)
        db.session.add(new_genre)
        db.session.commit()
        return redirect(url_for('staff.manage_genres'))

    # Render the form when the method is GET
    return render_template('staff/add_genre.html')


@staff_bp.route('/edit_genre/<int:genre_id>', methods=['GET', 'POST'])
@jwt_required()
def edit_genre(genre_id):
    if not is_staff():
        return redirect('/')  # Redirect to home or unauthorized page

    genre = Genre.query.get_or_404(genre_id)

    if request.method == 'POST':
        genre.genre_name = request.form['genre_name']
        db.session.commit()
        return redirect(url_for('staff.manage_genres'))

    # Render the edit form with existing genre data when method is GET
    return render_template('staff/edit_genre.html', genre=genre)



@staff_bp.route('/lending_transactions/create', methods=['GET', 'POST'])
@jwt_required()
def create_lending_transaction():
    if request.method == 'POST':
        member_id = request.form.get('member_id')
        resource_id = request.form.get('resource_id')
        due_date = request.form.get('due_date')  # Add a due date field in the form

        if not due_date:
            # flash('Due date is required.', 'danger')
            return redirect(url_for('staff.create_lending_transaction'))

        new_transaction = LendingTransaction(
            member_id=member_id,
            resource_id=resource_id,
            due_date=due_date,
            status='borrowed'  # Default status
        )
        db.session.add(new_transaction)
        db.session.commit()

        # flash('Lending transaction created successfully!', 'success')
        return redirect(url_for('staff.manage_lending_transactions'))  # Redirect after creation

    members = Member.query.all()
    resources = LibraryResource.query.all()
    return render_template('staff/create_lending_transactions.html', members=members, resources=resources)
