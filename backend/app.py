"""
Kos Management Dashboard - Flask Backend Application
Supports SQLite (development), PostgreSQL (production), and Google Cloud SQL (GCP)
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta
from models import db
from routes import auth_bp, rooms_bp, tenants_bp, payments_bp, expenses_bp, dashboard_bp

load_dotenv()


def create_app(config_name=None):
    """Application factory for Flask app creation."""
    app = Flask(__name__)

    # Configuration from environment variables
    # Supports: SQLite, PostgreSQL, Supabase, GCP Cloud SQL
    database_url = os.getenv('DATABASE_URL', 'sqlite:///kos.db')

    # For GCP Cloud SQL (optional)
    if os.getenv('GCP_PROJECT'):
        # GCP Cloud SQL Proxy configuration
        # Connection string: postgresql://user:password@/db?unix_socket=/cloudsql/PROJECT:REGION:INSTANCE
        pass  # SQLAlchemy handles unix_socket in connection string

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False

    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv(
        'JWT_SECRET_KEY',
        'dev-secret-key-change-in-production'
    )
    jwt_expiration = int(os.getenv('JWT_EXPIRATION_DAYS', 30))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=jwt_expiration)

    # Flask Configuration
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    app.config['ENV'] = os.getenv('FLASK_ENV', 'development')

    # Initialize extensions
    db.init_app(app)

    # CORS Configuration - allow configurable origins
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173')
    origins = [origin.strip() for origin in cors_origins.split(',')]
    CORS(app, resources={r"/api/*": {"origins": origins}})

    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(tenants_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(dashboard_bp)

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint for deployment monitoring."""
        return jsonify({
            'status': 'ok',
            'environment': os.getenv('FLASK_ENV', 'development'),
            'database': 'sqlite' if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI'] else 'postgresql'
        }), 200

    # API root endpoint
    @app.route('/api', methods=['GET'])
    def api_root():
        """API root endpoint with version info."""
        return jsonify({
            'message': 'Kos Management API',
            'version': '1.0.0',
            'status': 'active'
        }), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app


# Create app instance for development
app = create_app()


if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Environment: {app.config['ENV']}")

    # Run development server
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )
