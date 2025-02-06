from flask import Blueprint, render_template

# Create the Blueprint
lending_transactions_bp = Blueprint('lending_transactions', __name__, template_folder='../templates/lending_transactions')

@lending_transactions_bp.route('/')
def index():
    return render_template('lending_transactions/index.html')

@lending_transactions_bp.route('/create')
def create():
    return render_template('lending_transactions/create.html')

@lending_transactions_bp.route('lending_transactions/details/<int:id>')
def details(id):
    return render_template('lending_transactions/details.html', id=id)

@lending_transactions_bp.route('lending_transactions/edit/<int:id>/edit')
def edit(id):
    return render_template('lending_transactions/edit.html', id=id)
