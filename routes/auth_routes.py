from flask import Blueprint, render_template

# Create the Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')


@auth_bp.route('/login')
def login():
    return render_template('login.html')

@auth_bp.route('/register')
def register():
    return render_template('register.html')

@auth_bp.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')
