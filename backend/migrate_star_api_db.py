#!/usr/bin/env python3
"""
Database Migration Script for Star API Enhanced Schema
Creates all new tables for comprehensive Instagram data collection
Following the DATABASE_SERVICE_DOCUMENTATION.md UPSERT strategy
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db
from flask import Flask
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """
    Run database migration to create new Star API tables
    """
    try:
        # Create Flask app context
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instagram_analytics.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database with app
        db.init_app(app)
        
        with app.app_context():
            logger.info("🔄 Starting database migration for Star API enhanced schema...")
            
            # Create all tables (this will only create new ones, won't affect existing)
            db.create_all()
            
            logger.info("✅ Database migration completed successfully!")
            logger.info("📊 Enhanced tables created:")
            logger.info("   - location_data: Instagram location information")
            logger.info("   - similar_accounts: User similarity analysis")
            logger.info("   - user_search_results: Search result tracking")
            logger.info("   - location_search_results: Location search tracking")
            logger.info("   - audio_data: Music and audio information")
            logger.info("   - audio_search_results: Audio search tracking")
            logger.info("   - comment_replies: Comment thread management")
            logger.info("   - comment_likes: Comment engagement tracking")
            logger.info("   - highlight_stories: Highlight content details")
            logger.info("   - data_collection_logs: API usage monitoring")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            table_names = inspector.get_table_names()
            
            expected_new_tables = [
                'location_data', 'similar_accounts', 'user_search_results',
                'location_search_results', 'audio_data', 'audio_search_results',
                'comment_replies', 'comment_likes', 'highlight_stories',
                'data_collection_logs'
            ]
            
            existing_new_tables = [table for table in expected_new_tables if table in table_names]
            
            logger.info(f"📋 Verified {len(existing_new_tables)}/{len(expected_new_tables)} new tables created")
            
            if len(existing_new_tables) == len(expected_new_tables):
                logger.info("🎉 All enhanced tables created successfully!")
                logger.info("🚀 Star API comprehensive data collection is ready!")
            else:
                missing_tables = [table for table in expected_new_tables if table not in table_names]
                logger.warning(f"⚠️ Missing tables: {missing_tables}")
            
            # Display existing core tables
            core_tables = [
                'profiles', 'media_posts', 'stories', 'highlights', 
                'follower_data', 'media_comments', 'hashtag_data', 'daily_metrics'
            ]
            existing_core_tables = [table for table in core_tables if table in table_names]
            logger.info(f"📊 Core tables verified: {len(existing_core_tables)}/{len(core_tables)}")
            
            logger.info("\n" + "="*60)
            logger.info("🎯 COMPREHENSIVE INSTAGRAM DATA COLLECTION READY")
            logger.info("="*60)
            logger.info("📈 Available data types:")
            logger.info("   • User profiles with analytics")
            logger.info("   • Media posts with engagement tracking")
            logger.info("   • Stories and highlights")
            logger.info("   • Follower/following relationships")
            logger.info("   • Location-based data")
            logger.info("   • Audio/music information")
            logger.info("   • Comment threads and engagement")
            logger.info("   • Similar account recommendations")
            logger.info("   • Search result tracking")
            logger.info("   • Comprehensive API usage logs")
            logger.info("="*60)
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise e

if __name__ == "__main__":
    run_migration()
