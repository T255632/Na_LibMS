from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from models import db
from models import init_db
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


if __name__ == '__main__':
    app.run(port=5000, debug=bool(int(os.getenv('FLASK_DEBUG', 1))))
