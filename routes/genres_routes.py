from flask import Blueprint, render_template

# Create the Blueprint
genres_bp = Blueprint('genres', __name__, template_folder='../templates/genres')

@genres_bp.route('/')
def index():
    return render_template('genres/index.html')

@genres_bp.route('/create')
def create():
    return render_template('genres/create.html')

@genres_bp.route('/<int:id>')
def details(id):
    return render_template('genres/details.html', id=id)

@genres_bp.route('/<int:id>/edit')
def edit(id):
    return render_template('genres/edit.html', id=id)
