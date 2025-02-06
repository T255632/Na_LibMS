from flask import Blueprint, render_template

# Create the Blueprint
library_resources_bp = Blueprint('library_resources', __name__, template_folder='../templates/library_resources')

@library_resources_bp.route('/')
def index():
    return render_template('library_resources/index.html')

@library_resources_bp.route('/create')
def create():
    return render_template('library_resources/create.html')

@library_resources_bp.route('library_resources/details/<int:id>')
def details(id):
    return render_template('library_resources/details.html', id=id)

@library_resources_bp.route('library_resources/edit/<int:id>/edit')
def edit(id):
    return render_template('library_resources/edit.html', id=id)
