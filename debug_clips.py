#!/usr/bin/env python3
"""
Debug clips data structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.star_api_data_service import StarAPIService

def debug_clips():
    # Initialize the service
    api_service = StarAPIService()
    
    # Get clips data for NASA
    print("🔍 Debugging clips data structure...")
    result = api_service.get_user_clips("nasa", count=3)
    
    if result['success']:
        print("✅ Clips data retrieved successfully")
        response_body = result['data']['response']['body']
        
        if 'items' in response_body:
            items = response_body['items']
            print(f"📊 Found {len(items)} clips")
            
            for i, item in enumerate(items[:2]):  # Just check first 2
                print(f"\n--- Clip {i+1} ---")
                print(f"Keys: {list(item.keys())}")
                print(f"ID: {item.get('id')}")
                print(f"Shortcode: {item.get('shortcode')}")
                print(f"Media Type: {item.get('media_type')}")
                print(f"Video URL: {item.get('video_url')}")
                print(f"Taken at: {item.get('taken_at_timestamp')}")
        else:
            print("❌ No items found in clips response")
            print(f"Response keys: {list(response_body.keys())}")
    else:
        print(f"❌ Failed to get clips: {result.get('error')}")

if __name__ == "__main__":
    debug_clips()
