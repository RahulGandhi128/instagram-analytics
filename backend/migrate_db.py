"""
Database Migration Script
Recreates database tables with new schema
"""
import os
import sys
from flask import Flask
from models.database import db

def migrate_database():
    """Recreate database with new schema"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instagram_analytics.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        print("🔄 Dropping existing tables...")
        db.drop_all()
        
        print("🔧 Creating new tables with updated schema...")
        db.create_all()
        
        print("✅ Database migration completed successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📊 Created tables: {', '.join(tables)}")
        
        return True

if __name__ == "__main__":
    try:
        migrate_database()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
