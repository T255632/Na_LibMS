from flask import Blueprint, render_template

# Create the Blueprint
members_bp = Blueprint('members', __name__, template_folder='../templates/members')

@members_bp.route('/')
def index():
    return render_template('members/index.html')

@members_bp.route('/create')
def create():
    return render_template('members/create.html')

@members_bp.route('members/details/<int:id>')
def details(id):
    return render_template('details.html', id=id)

@members_bp.route('members/edit/<int:id>/edit')
def edit(id):
    return render_template('edit.html', id=id)
