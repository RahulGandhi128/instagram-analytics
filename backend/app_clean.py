"""
Instagram Analytics Flask Application - Clean Setup
"""
from flask import Flask
from flask_cors import CORS
from models.database import db
from api.routes import register_blueprints
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database configuration - Clean SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instagram_analytics.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    print("Using clean SQLite database")
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register API blueprints
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'database': 'connected',
            'version': '1.0.0'
        }, 200
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
    
    return app

app = create_app()

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=True
    )
