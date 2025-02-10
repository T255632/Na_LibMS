from flask import Flask, jsonify, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import ProgrammingError
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db
from models import init_db
from dotenv import load_dotenv
import os
from triggers.generate_admin_notifications import create_notification_triggers, DuplicateObject

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database Configuration
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')  # Default to localhost if not set
DB_PORT = os.getenv('POSTGRES_PORT', '5432')       # Default to 5432 if not set
DB_CONTAINER = os.getenv('DB_CONTAINER')




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

# Create notification triggers (within an app context)
with app.app_context():
    try:
        create_notification_triggers()
    except DuplicateObject as e:
        # Handle DuplicateObject (trigger already exists)
        print(f"Duplicate trigger error: {e}")
    except ProgrammingError as e:
        # Handle other SQL programming errors
        print(f"Programming error: {e}")
    except Exception as e:
        # Catch all other exceptions
        print(f"An unexpected error occurred: {e}")

        

# Define a route for the index page
@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(port=5000, debug=bool(int(os.getenv('FLASK_DEBUG', 1))))
