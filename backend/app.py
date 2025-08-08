"""
Instagram Analytics Flask Application
"""
from flask import Flask
from flask_cors import CORS
from models.database import db
from api.routes import api_bp
import os
from dotenv import load_dotenv
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    print("APScheduler not available - install with: pip install APScheduler")

from services.instagram_service import InstagramAnalyticsService

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database configuration - PostgreSQL with SQLite fallback
    if os.getenv('USE_SQLITE', 'False').lower() == 'true' or not os.getenv('DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instagram_analytics.db'
        print("Using SQLite database")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        print("Using PostgreSQL database")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Enable CORS for React frontend
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check route
    @app.route('/')
    def index():
        return {
            'message': 'Instagram Analytics API',
            'version': '1.0.0',
            'status': 'running'
        }
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for Docker monitoring"""
        from datetime import datetime
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'instagram-analytics-backend',
            'database': 'connected'
        }, 200
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    
    # Setup background scheduler for automated data fetching
    if SCHEDULER_AVAILABLE:
        setup_scheduler(app)
    
    return app

def setup_scheduler(app):
    """Setup background scheduler for automated tasks"""
    scheduler = BackgroundScheduler()
    
    def scheduled_data_fetch():
        """Scheduled function to fetch Instagram data"""
        with app.app_context():
            try:
                api_key = os.getenv('API_KEY')
                if not api_key:
                    print("API_KEY not found in environment variables")
                    return
                
                service = InstagramAnalyticsService(api_key)
                service.fetch_all_data()
                print("Scheduled data fetch completed")
            except Exception as e:
                print(f"Error in scheduled data fetch: {e}")
    
    # Schedule data fetching every 6 hours
    scheduler.add_job(
        func=scheduled_data_fetch,
        trigger="interval",
        hours=6,
        id='fetch_instagram_data'
    )
    
    # Start scheduler
    try:
        scheduler.start()
        print("Background scheduler started")
    except Exception as e:
        print(f"Error starting scheduler: {e}")

app = create_app()

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
