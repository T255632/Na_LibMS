from flask import Blueprint, render_template

# Create the Blueprint
staff_bp = Blueprint('staff', __name__, template_folder='../templates/staff')

@staff_bp.route('/')
def index():
    return render_template('staff/index.html')

@staff_bp.route('/create')
def create():
    return render_template('staff/create.html')

@staff_bp.route('staff/details/<int:id>')
def details(id):
    return render_template('staff/details.html', id=id)

@staff_bp.route('staff/edit/<int:id>/edit')
def edit(id):
    return render_template('edit.html', id=id)
