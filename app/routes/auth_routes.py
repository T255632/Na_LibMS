import logging
from flask import Blueprint, request, redirect, render_template, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from models import db
from models.user_roles import UserRole 
from models.staff import Staff
from models.members import Member
import random
import string
import datetime


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        logger.debug(f"Login attempt for username: {username}")

        # Check for staff (Admin or Staff)
        staff = Staff.query.filter_by(name=username).first()
        if staff:
            logger.debug(f"Staff found: {staff.name}")
        else:
            logger.warning(f"No staff found with username: {username}")

        user_role = UserRole.query.filter_by(staff_id=staff.staff_id).first() if staff else None
        if user_role:
            logger.debug(f"User role found for {username}: {user_role.role}")
        else:
            logger.warning(f"No user role found for staff: {username}")

        if user_role and check_password_hash(user_role.password_hash, password):
            logger.info(f"Login successful for staff: {username}")
            access_token = create_access_token(identity=str(staff.staff_id), additional_claims={
                'user_id': user_role.user_id,
                'role': user_role.role,
                'staff_id': str(staff.staff_id)
            })
            dashboard_route = '/admin/admin_dashboard' if user_role.role == 'Admin' else '/staff/dashboard'
            response = make_response(redirect(dashboard_route))
            response.set_cookie('access_token', access_token, httponly=True, secure=False)  # Use secure=True in production
            return response
        else:
            logger.warning(f"Invalid credentials for staff: {username}")

        # Fallback to Member
        member = Member.query.filter_by(name=username).first()
        if member:
            logger.debug(f"Member found: {member.name}")
        else:
            logger.warning(f"No member found with username: {username}")

        if member and check_password_hash(member.password_hash, password):
            logger.info(f"Login successful for member: {username}")
            access_token = create_access_token(identity=str(member.member_id), additional_claims={
                'member_id': str(member.member_id),
                'role': 'Member'
            })
            response = make_response(redirect('/member/member_dashboard'))
            response.set_cookie('access_token', access_token, httponly=True, secure=False)
            return response
        else:
            logger.warning(f"Invalid credentials for member: {username}")

        return render_template('auth/login.html', error='Invalid credentials')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
        status = request.form.get('status')

        # Generate membership number
        membership_number = generate_membership_number(username)

        logger.debug(f"Registration attempt for username: {username} with membership number: {membership_number}")

        if not username or not email or not password:
            logger.warning("Username, email, or password missing.")
            return render_template('auth/register.html', error='Please fill in all required fields.')

        # Check if email already exists
        if Member.query.filter_by(email=email).first():
            logger.warning(f"Email already exists: {email}")
            return render_template('auth/register.html', error='Email already exists.')

        password_hash = generate_password_hash(password)
        logger.debug(f"Generated password hash for user: {username}")

        # Create new member
        new_member = Member(
            membership_number=membership_number,
            name=username,
            email=email,
            phone=phone,
            address=address,
            status=status,
            password_hash=password_hash
        )
        db.session.add(new_member)
        db.session.commit()
        logger.info(f"New member created: {username}")

        return redirect('/auth/login')

    return render_template('auth/register.html')


def generate_membership_number(username):
    """Generate a unique membership number based on the username."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    membership_number = f"{username[:3].upper()}-{timestamp}-{random_string}"
    return membership_number


@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        logger.debug(f"Password reset request for email: {email}")
        # Add password recovery logic here
        return render_template('auth/forgot_password.html', message='Password reset instructions sent.')
    return render_template('auth/forgot_password.html')


@auth_bp.route('/logout')
@jwt_required()
def logout():
    try:
        logger.debug(f"User logging out. JWT identity: {get_jwt_identity()}")
        response = make_response(redirect('/auth/login'))
        response.delete_cookie('access_token')
        return response
    except Exception:
        # Redirect to the homepage if the token is missing
        return redirect('/')



