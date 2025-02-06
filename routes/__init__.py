from flask import Blueprint
from .auth_routes import auth_bp
from .genres_routes import genres_bp
from .lending_transactions_routes import lending_transactions_bp
from .library_resources_routes import library_resources_bp
from .members_routes import members_bp
from .staff_routes import staff_bp

def init_app(app):
    # List of blueprints with their URL prefixes
    blueprints = [
        (auth_bp, '/auth'),
        (genres_bp, '/genres'),
        (lending_transactions_bp, '/lending_transactions'),
        (library_resources_bp, '/library_resources'),
        (members_bp, '/members'),
        (staff_bp, '/staff')
    ]

    # Register each blueprint using a loop
    for bp, prefix in blueprints:
        app.register_blueprint(bp, url_prefix=prefix)
