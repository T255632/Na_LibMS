from flask import Blueprint, render_template, redirect, request, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
import json 
from models import db
from models.staff import Staff
from models.members import Member
from models.genres import Genre
from models.library_resources import LibraryResource
from models.lending_transactions import LendingTransaction
from models.user_roles import UserRole
from models.borrowing_rules import BorrowingRule

# Create the Blueprint for Admin Routes
admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

# Helper function to check admin role
def is_admin():
    current_user = json.loads(get_jwt_identity())
    return current_user['role'] == 'Admin'

# Admin Dashboard Route
@admin_bp.route('/admin_dashboard')
@jwt_required()
def admin_dashboard():
    if not is_admin():
        return redirect('/')  # Redirect to home or an unauthorized page

    staff_members = Staff.query.all()
    return render_template('admin/index.html', staff_members=staff_members)

# Staff Management Route
@admin_bp.route('/staff_management')
@jwt_required()
def staff_management():
    if not is_admin():
        return redirect('/')

    staff_members = Staff.query.all()
    return render_template('admin/staff_management.html', staff_members=staff_members)

@admin_bp.route('/member_management')
@jwt_required()
def member_management():
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page

    members = Member.query.all()  # Get all members from the database
    return render_template('admin/member_management.html', members=members)



@admin_bp.route('/add_member', methods=['GET', 'POST'])
@jwt_required()
def add_member():
    if not is_admin():
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

        return redirect(url_for('admin.member_management'))  # Redirect to member management page
    
    return render_template('admin/add_member.html')



@admin_bp.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
@jwt_required()
def edit_member(member_id):
    if not is_admin():
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

        return redirect(url_for('admin.member_management'))  # Redirect to member management page
    
    # Render the edit form pre-filled with the current member details
    return render_template('admin/edit_member.html', member=member)



@admin_bp.route('/delete_member/<int:member_id>', methods=['POST'])
@jwt_required()
def delete_member(member_id):
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page
    
    # Find the member by ID
    member = Member.query.get_or_404(member_id)
    
    # Delete the member from the database
    db.session.delete(member)
    db.session.commit()

    return redirect(url_for('admin.member_management'))  # Redirect to member management page



# Library Resource Management Route
@admin_bp.route('/resources_management')
@jwt_required()
def resources_management():
    if not is_admin():
        return redirect('/')

    resources = LibraryResource.query.all()
    return render_template('admin/resources_management.html', resources=resources)

# Borrowing Rules Configuration Route
@admin_bp.route('/borrowing_rules')
@jwt_required()
def borrowing_rules():
    if not is_admin():
        return redirect('/')

    rules = UserRole.query.all()  # Assuming borrowing rules are linked with roles
    return render_template('admin/borrowing_rules.html', rules=rules)

# Lending Transactions Management Route
@admin_bp.route('/lending_transactions')
@jwt_required()
def lending_transactions():
    if not is_admin():
        return redirect('/')

    transactions = LendingTransaction.query.all()
    return render_template('admin/lending_transactions.html', transactions=transactions)

# Password Policy Configuration Route
@admin_bp.route('/password_policy')
@jwt_required()
def password_policy():
    if not is_admin():
        return redirect('/')

    return render_template('admin/password_policy.html')


@admin_bp.route('/add_staff', methods=['GET', 'POST'])
@jwt_required()
def add_staff():
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page
    
    if request.method == 'POST':
        # Get the data from the form
        name = request.form['name']
        qualification = request.form['qualification']
        experience = request.form['experience']
        skill_set = request.form['skill_set']
        grade = request.form['grade']
        contact_info = json.dumps(request.form['contact_info'])
        role = request.form['role']
        status = True  # Default to active status
        
        # Create the new staff member
        new_staff = Staff(
            name=name,
            qualification=qualification,
            experience=experience,
            skill_set=skill_set,
            grade=grade,
            contact_info=contact_info,
            role=role,
            status=status
        )

        db.session.add(new_staff)
        db.session.commit()

        # Create the user role for the staff member with a default password
        new_user_role = UserRole(
            staff_id=new_staff.staff_id,
            role=role,
            password_hash=generate_password_hash('12345678')  # Hashing the default password
        )

        db.session.add(new_user_role)
        db.session.commit()

        return redirect(url_for('admin.staff_management'))  # Redirect to staff management page
    
    return render_template('admin/add_staff.html')

@admin_bp.route('/edit_staff/<int:staff_id>', methods=['GET', 'POST'])
@jwt_required()
def edit_staff(staff_id):
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page
    
    staff_member = Staff.query.get_or_404(staff_id)
    
    if request.method == 'POST':
        # Get the updated data from the form
        staff_member.name = request.form['name']
        staff_member.qualification = request.form['qualification']
        staff_member.experience = request.form['experience']
        staff_member.skill_set = request.form['skill_set']
        staff_member.grade = request.form['grade']
        staff_member.contact_info = json.dumps(request.form['contact_info'])
        staff_member.role = request.form['role']
        
        db.session.commit()
        
        return redirect(url_for('admin.staff_management'))  # Redirect back to staff management page
    
    return render_template('admin/edit_staff.html', staff=staff_member)


@admin_bp.route('/delete_staff/<int:staff_id>', methods=['POST'])
@jwt_required()
def delete_staff(staff_id):
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page
    
    staff_member = Staff.query.get_or_404(staff_id)
    db.session.delete(staff_member)
    db.session.commit()
    
    return redirect(url_for('admin.staff_management'))  # Redirect back to staff management page


@admin_bp.route('/manage_genres', methods=['GET'])
@jwt_required()
def manage_genres():
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page
    
    genres = Genre.query.all()
    return render_template('admin/manage_genres.html', genres=genres)


@admin_bp.route('/add_genre', methods=['GET', 'POST'])
@jwt_required()
def add_genre():
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page

    if request.method == 'POST':
        genre_name = request.form['genre_name']
        new_genre = Genre(genre_name=genre_name)
        db.session.add(new_genre)
        db.session.commit()
        return redirect(url_for('admin.manage_genres'))

    # Render the form when the method is GET
    return render_template('admin/add_genre.html')


@admin_bp.route('/edit_genre/<int:genre_id>', methods=['GET', 'POST'])
@jwt_required()
def edit_genre(genre_id):
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page

    genre = Genre.query.get_or_404(genre_id)

    if request.method == 'POST':
        genre.genre_name = request.form['genre_name']
        db.session.commit()
        return redirect(url_for('admin.manage_genres'))

    # Render the edit form with existing genre data when method is GET
    return render_template('admin/edit_genre.html', genre=genre)


@admin_bp.route('/delete_genre/<int:genre_id>', methods=['POST'])
@jwt_required()
def delete_genre(genre_id):
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page

    genre = Genre.query.get_or_404(genre_id)
    db.session.delete(genre)
    db.session.commit()
    return redirect(url_for('admin.manage_genres'))



# Resource Management Routes
@admin_bp.route('/manage_resources', methods=['GET'])
@jwt_required()
def manage_resources():
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page
    
    resources = LibraryResource.query.all()
    return render_template('admin/manage_resources.html', resources=resources)

def get_current_user():
    user_identity = get_jwt_identity()

    # Parse the JSON string to a dictionary if needed
    if isinstance(user_identity, str):
        user_identity = json.loads(user_identity)

    staff_id = user_identity.get('staff_id')  # Extract just the staff_id
    return Staff.query.get(staff_id)

@admin_bp.route('/add_resource', methods=['GET', 'POST'])
@jwt_required()
def add_resource():
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page

    # Fetch all genres to populate the dropdown list
    genres = Genre.query.all()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre_id = request.form['genre_id']
        resource_type = request.form['resource_type']
        format = request.form['format']
        location = request.form['location']
        items = int(request.form['items'])  # New field added
        added_by_staff_id = get_current_user().staff_id
        available = True  # Set to True by default

        if items < 0:
            return "Items cannot be negative", 400

        new_resource = LibraryResource(
            title=title,
            author=author,
            genre_id=genre_id,
            resource_type=resource_type,
            format=format,
            location=location,
            items=items,  # Assign items
            added_by_staff_id=added_by_staff_id,
            available=available
        )
        db.session.add(new_resource)
        db.session.commit()
        return redirect(url_for('admin.resources_management'))  # Redirect to resources management page

    return render_template('admin/add_resource.html', genres=genres)


def get_genre_id_by_name(genre_name):
    print(f"Searching for genre: {genre_name}")  # Debugging line
    genre = Genre.query.filter_by(genre_name=genre_name).first()
    if not genre:
        raise ValueError(f"Genre '{genre_name}' not found.")
    return genre.genre_id

@admin_bp.route('/edit_resource/<int:resource_id>', methods=['GET', 'POST'])
@jwt_required()
def edit_resource(resource_id):
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page

    resource = LibraryResource.query.get_or_404(resource_id)
    genres = Genre.query.all()  # Fetch all genres to populate the genre dropdown

    if request.method == 'POST':
        resource.title = request.form['title']
        resource.author = request.form['author']

        # Using helper function to get genre_id
        genre_name = request.form.get('genre_name')
        genre_id = get_genre_id_by_name(genre_name)

        if genre_id:
            resource.genre_id = genre_id
        else:
            return "Genre not found", 400  # Handle invalid genre

        resource.resource_type = request.form['resource_type']
        resource.format = request.form['format']
        resource.location = request.form['location']

        # Update items
        items = int(request.form['items'])
        if items < 0:
            return "Items cannot be negative", 400
        resource.items = items

        db.session.commit()
        return redirect(url_for('admin.resources_management'))  # Redirect to resources management page

    return render_template('admin/edit_resource.html', resource=resource, genres=genres)

@admin_bp.route('/delete_resource/<int:resource_id>', methods=['POST'])
@jwt_required()
def delete_resource(resource_id):
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page

    resource = LibraryResource.query.get_or_404(resource_id)
    db.session.delete(resource)
    db.session.commit()
    return redirect(url_for('admin.resources_management'))  # Redirect to resources management page



# Borrowing Rules Management Route
@admin_bp.route('/manage_borrowing_rules')
@jwt_required()
def manage_borrowing_rules():
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page
    
    borrowing_rules = BorrowingRule.query.all()
    return render_template('admin/manage_borrowing_rules.html', borrowing_rules=borrowing_rules)

# Add Borrowing Rule Route
@admin_bp.route('/add_borrowing_rule', methods=['GET', 'POST'])
@jwt_required()
def add_borrowing_rule():
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page

    if request.method == 'POST':
        resource_type = request.form['resource_type']
        max_borrow_duration = request.form['max_borrow_duration']
        reminder_intervals = json.dumps(request.form.getlist('reminder_intervals'))  # Collecting multiple intervals
        
        new_borrowing_rule = BorrowingRule(
            resource_type=resource_type,
            max_borrow_duration=max_borrow_duration,
            reminder_intervals=reminder_intervals
        )
        
        db.session.add(new_borrowing_rule)
        db.session.commit()

        return redirect(url_for('admin.manage_borrowing_rules'))  # Redirect to borrowing rules management page

    return render_template('admin/add_borrowing_rule.html')

# Edit Borrowing Rule Route
@admin_bp.route('/edit_borrowing_rule/<int:rule_id>', methods=['GET', 'POST'])
@jwt_required()
def edit_borrowing_rule(rule_id):
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page

    rule = BorrowingRule.query.get_or_404(rule_id)

    if request.method == 'POST':
        rule.resource_type = request.form['resource_type']
        rule.max_borrow_duration = request.form['max_borrow_duration']
        rule.reminder_intervals = json.dumps(request.form.getlist('reminder_intervals'))  # Collecting multiple intervals
        
        db.session.commit()
        
        return redirect(url_for('admin.manage_borrowing_rules'))  # Redirect to borrowing rules management page

    return render_template('admin/edit_borrowing_rule.html', rule=rule)

# Delete Borrowing Rule Route
@admin_bp.route('/delete_borrowing_rule/<int:rule_id>', methods=['POST'])
@jwt_required()
def delete_borrowing_rule(rule_id):
    if not is_admin():
        return redirect('/')  # Redirect to home or unauthorized page

    rule = BorrowingRule.query.get_or_404(rule_id)
    db.session.delete(rule)
    db.session.commit()
    
    return redirect(url_for('admin.manage_borrowing_rules'))  # Redirect to borrowing rules management page
