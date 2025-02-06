from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import json
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models import init_db
from models.staff import Staff
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database Configuration
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')  # Default to localhost if not set
DB_PORT = os.getenv('POSTGRES_PORT', '5432')       # Default to 5432 if not set

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'  # Ensure it matches the cookie name
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF for now (optional for testing)


app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Make sure to set this in your .env file
jwt = JWTManager(app)



# Initialize Database
db.init_app(app)

from routes import init_app

init_db(app)

# Register Blueprints
init_app(app)  # <--- Add this line

# Define a route for the index page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_staff_members', methods=['GET'])
@jwt_required()
def get_staff_members():
    current_user = json.loads(get_jwt_identity())
    print("Current User:", current_user)  # Debugging line

    if current_user['role'] != 'Admin':
        print("Unauthorized Access Attempt:", current_user)
        return jsonify({'message': 'Unauthorized'}), 401

    staff_members = Staff.query.all()

    staff_data = [{
        'staff_id': staff.staff_id,
        'name': staff.name,
        'role': staff.role
    } for staff in staff_members]

    return jsonify({'staff_members': staff_data})



if __name__ == '__main__':
    app.run(port=5000, debug=bool(int(os.getenv('FLASK_DEBUG', 1))))
