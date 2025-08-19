#!/usr/bin/env python3
"""
Simple Star API Database Collector - Windows Compatible
Unicode-safe version for Windows command prompt
"""

import sys
import os
import json
from datetime import datetime, date, timezone
import pytz
import time
import re
from typing import Dict, List, Tuple, Optional, Any

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from dotenv import load_dotenv
    import requests
    from flask import Flask
    from models.database import (
        db, Profile, MediaPost, Story, MediaComment, 
        FollowerData, HashtagData, ApiRequestLog
    )
    
    # Load environment variables
    load_dotenv()
    
    def run_simple_collection():
        """Run simple data collection without Unicode characters"""
        print("STAR API DATABASE COLLECTOR")
        print("=" * 50)
        
        # Get API key
        api_key = os.getenv('RAPID_API_KEY') or os.getenv('API_KEY')
        if not api_key:
            print("Error: API key not found")
            return False
        
        print(f"API Key: {api_key[:10]}...")
        
        # Initialize Flask app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.path.dirname(__file__), "backend", "instance", "instagram_analytics.db")}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        db.init_app(app)
        
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            print("Database tables verified")
            
            # Simple API test
            try:
                headers = {
                    'X-RapidAPI-Key': api_key,
                    'X-RapidAPI-Host': 'instagram-scraper-api2.p.rapidapi.com'
                }
                
                url = "https://instagram-scraper-api2.p.rapidapi.com/v1.2/instagram/user/get_web_profile_info"
                params = {"username_or_id_or_url": "nasa"}
                
                print("Making API request...")
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data and 'user' in data['data']:
                        user_data = data['data']['user']
                        
                        print("API request successful!")
                        print(f"Profile: @{user_data.get('username', 'unknown')}")
                        print(f"Followers: {user_data.get('edge_followed_by', {}).get('count', 0):,}")
                        print(f"Media Count: {user_data.get('edge_owner_to_timeline_media', {}).get('count', 0):,}")
                        
                        # Simple profile storage test
                        try:
                            profile_data = {
                                'instagram_id': str(user_data.get('id', 'test_id')),
                                'username': user_data.get('username', 'nasa'),
                                'full_name': user_data.get('full_name', 'NASA'),
                                'biography': user_data.get('biography', ''),
                                'followers_count': user_data.get('edge_followed_by', {}).get('count', 0),
                                'following_count': user_data.get('edge_follow', {}).get('count', 0),
                                'media_count': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                                'is_verified': user_data.get('is_verified', False),
                                'is_private': user_data.get('is_private', False),
                                'profile_pic_url': user_data.get('profile_pic_url', ''),
                                'external_url': user_data.get('external_url', '')
                            }
                            
                            profile, created = Profile.upsert(**profile_data)
                            
                            if created:
                                print(f"Created new profile: {profile.username}")
                            else:
                                print(f"Updated existing profile: {profile.username}")
                            
                            # Count records
                            profile_count = Profile.query.count()
                            media_count = MediaPost.query.count()
                            api_log_count = ApiRequestLog.query.count()
                            
                            print("\\nDatabase Summary:")
                            print(f"  Profiles: {profile_count}")
                            print(f"  Media Posts: {media_count}")
                            print(f"  API Logs: {api_log_count}")
                            
                            print("\\nCollection completed successfully!")
                            return True
                            
                        except Exception as e:
                            print(f"Database storage error: {e}")
                            return False
                    else:
                        print("Invalid API response structure")
                        return False
                else:
                    print(f"API request failed: HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"API request error: {e}")
                return False
    
    if __name__ == "__main__":
        success = run_simple_collection()
        if success:
            print("\\nDemo completed successfully!")
        else:
            print("\\nDemo failed!")
            sys.exit(1)

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)
