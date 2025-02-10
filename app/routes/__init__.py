from flask import Blueprint
from .members_routes import members_bp
from .admin_routes import admin_bp
from .staff_routes import staff_bp

from .auth_routes import auth_bp

def init_app(app):
    # List of blueprints with their URL prefixes
    blueprints = [
        (auth_bp, '/auth'),
        (admin_bp, '/admin'),
        (members_bp, '/member'),
        (staff_bp, '/staff')
        
    ]

    # Register each blueprint using a loop
    for bp, prefix in blueprints:
        app.register_blueprint(bp, url_prefix=prefix)
