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

@staff_bp.route('/member_management')
@jwt_required()
def member_management():
    if not is_staff():
        return redirect('/')  # Redirect to home or unauthorized page

    members = Member.query.all()  # Get all members from the database
    return render_template('staff/member_management.html', members=members)



@staff_bp.route('/add_member', methods=['GET', 'POST'])
@jwt_required()
def add_member():
    if not is_staff():
        return redirect('/')  # Redirect to home or unauthorized page
    
    if request.method == 'POST':
        # Get the data from the form
        name = request.form['name']
        membership_number = request.form['membership_number']
        address = json.dumps(request.form['address'])
        email = request.form['email']
        phone = request.form['phone']
        status = request.form['status']
        borrowing_behavior = json.dumps(request.form['borrowing_behavior'])
        
        # Create the new member
        new_member = Member(
            name=name,
            membership_number=membership_number,
            address=address,
            email=email,
            phone=phone,
            status=status,
            borrowing_behavior=borrowing_behavior
        )

        db.session.add(new_member)
        db.session.commit()

        return redirect(url_for('staff.profile'))  # Redirect to member management page
    
    return render_template('staff/add_member.html')





@staff_bp.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
@jwt_required()
def edit_member(member_id):
    if not is_staff():
        return redirect('/')  # Redirect to home or unauthorized page
    
    # Get the member by ID
    member = Member.query.get_or_404(member_id)
    
    if request.method == 'POST':
        # Get the updated data from the form
        member.name = request.form['name']
        member.membership_number = request.form['membership_number']
        member.address = json.dumps(request.form['address'])
        member.email = request.form['email']
        member.phone = request.form['phone']
        member.status = request.form['status']
        member.borrowing_behavior = json.dumps(request.form['borrowing_behavior'])

        # Commit the changes to the database
        db.session.commit()

        return redirect(url_for('staff.member_management'))  # Redirect to member management page
    
    # Render the edit form pre-filled with the current member details
    return render_template('staff/edit_member.html', member=member)




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
    return render_template('staff/manage_lending_transactions.html', lending_transactions=lending_transactions)


@staff_bp.route('/lend_book', methods=['GET', 'POST'])
@jwt_required()
def add_lending_transaction():
    if not is_staff():
        return redirect('/')

    staff_member = get_current_user()
    if not staff_member:
        return redirect('/')  # Redirect if staff not found

    if request.method == 'POST':
        try:
            member_id = int(request.form.get('member_id'))
            resource_id = int(request.form.get('resource_id'))
        except (ValueError, TypeError):
            return "Invalid member or resource ID", 400

        # Validate member existence
        member = Member.query.get(member_id)
        if not member:
            return "Member not found", 404

        # Validate resource existence
        resource = LibraryResource.query.get(resource_id)
        if not resource:
            return "Resource not found", 404

        # Check borrowing rule based on resource type
        borrowing_rule = BorrowingRule.query.filter_by(resource_type=resource.resource_type).first()
        if not borrowing_rule:
            return "Borrowing rule not found for this resource type", 404

        max_borrow_duration = borrowing_rule.max_borrow_duration
        due_date = datetime.now() + timedelta(days=max_borrow_duration)

        # Check if the resource is available and has enough items
        if resource.items <= 0 or not resource.available:
            return "Resource is currently unavailable", 400

        # Create new lending transaction
        new_transaction = LendingTransaction(
            member_id=member_id,
            resource_id=resource_id,
            due_date=due_date,
            status='borrowed',
            staff_id=staff_member.staff_id
        )

        # Update resource availability if needed
        resource.items -= 1
        if resource.items == 0:
            resource.available = False

        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for('staff.manage_lending_transactions'))

    members = Member.query.all()
    resources = LibraryResource.query.filter(LibraryResource.available == True).all()  # Only show available resources
    return render_template('staff/create_lending_transactions.html', members=members, resources=resources)


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

