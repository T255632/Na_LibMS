from flask import Blueprint, request, redirect, render_template, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import json
from models import db
from models.user_roles import UserRole 
from models.staff import Staff
from models.members import Member
# Create the Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check in staff first
        user = UserRole.query.join(Staff).filter(Staff.name == username).first()

        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=json.dumps({
            'user_id': user.user_id,
            'role': user.role,
            'staff_id': user.staff_id
        }))

            response = make_response(redirect(f'/{user.role.lower()}/{user.role.lower()}_dashboard'))
            response.set_cookie('access_token', access_token, httponly=True, secure=False)
            return response

        # Fallback to Member
        member = Member.query.filter(Member.name == username).first()
        if member and check_password_hash(member.password_hash, password):
            access_token = create_access_token(identity={
                'member_id': member.member_id,
                'role': 'Member'
            })

            response = make_response(redirect('/member/member_dashboard'))
            response.set_cookie('access_token', access_token, httponly=True, secure=True)  # set secure=True in production
            return response

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # role = request.form['role']  # Admin, Staff, Member
        role = 'Member'

        # Hash the password
        password_hash = generate_password_hash(password)

        if role in ['Admin', 'Staff']:
            new_staff = Staff(name=username, role=role)
            db.session.add(new_staff)
            db.session.commit()

            new_user = UserRole(role=role, password_hash=password_hash, staff_id=new_staff.staff_id)
            db.session.add(new_user)

        elif role == 'Member':
            new_member = Member(name=username, password_hash=password_hash)
            db.session.add(new_member)

        db.session.commit()
        return redirect('/auth/login')

    return render_template('register.html')

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # Add logic to handle password recovery
        return render_template('forgot_password.html', message='Password reset instructions sent.')
    return render_template('forgot_password.html')


@auth_bp.route('/logout')
@jwt_required()
def logout():
    response = make_response(redirect('/auth/login'))
    response.delete_cookie('access_token')
    return response