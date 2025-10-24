import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from models import db
from routes import auth_bp, rooms_bp, tenants_bp, payments_bp, expenses_bp, dashboard_bp

load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///kos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')

# Initialize extensions
db.init_app(app)
CORS(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(rooms_bp)
app.register_blueprint(tenants_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(dashboard_bp)


@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}, 200


@app.route('/', methods=['GET'])
def index():
    return {'message': 'Kos Management API'}, 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
