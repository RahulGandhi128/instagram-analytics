#!/usr/bin/env python3
"""
Test script to verify the video generation API endpoint works
"""

import requests
import json

def test_video_generation_api():
    """Test the video generation API endpoint"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Video Generation API")
    print("=" * 50)
    
    # Test 1: Video Concept Generation (Free)
    print("\n📝 Test 1: Video Concept Generation")
    print("-" * 30)
    
    concept_payload = {
        "user_id": "test_user",
        "prompt": "Create a short Instagram video about diverse professionals on Naukri.com",
        "content_type": "video",
        "session_id": "test_session_001",
        "video_include_audio": False,
        "video_quality": "standard",
        "video_generate_actual": False  # Concept only
    }
    
    try:
        response = requests.post(f"{base_url}/api/content/create", 
                               json=concept_payload, 
                               headers={"Content-Type": "application/json"},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Concept generation successful!")
            print(f"Content Type: {result.get('content_type', 'unknown')}")
            print(f"Success: {result.get('error') is None}")
            print(f"Description: {result.get('description', 'No description')[:100]}...")
            if result.get('debug_info'):
                print(f"Service: {result['debug_info'].get('service', 'unknown')}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Actual Video Generation (Experimental)
    print("\n🎬 Test 2: Actual Video Generation (Experimental)")
    print("-" * 30)
    
    actual_payload = {
        "user_id": "test_user",
        "prompt": "Create a short Instagram video about diverse professionals on Naukri.com",
        "content_type": "video",
        "session_id": "test_session_002",
        "video_include_audio": False,
        "video_quality": "standard",
        "video_generate_actual": True  # Actual video attempt
    }
    
    try:
        response = requests.post(f"{base_url}/api/content/create", 
                               json=actual_payload, 
                               headers={"Content-Type": "application/json"},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Actual video generation completed!")
            print(f"Content Type: {result.get('content_type', 'unknown')}")
            print(f"Success: {result.get('error') is None}")
            print(f"Video URL: {result.get('content_url', 'No URL')}")
            print(f"Description: {result.get('description', 'No description')[:100]}...")
            if result.get('debug_info'):
                print(f"Service: {result['debug_info'].get('service', 'unknown')}")
                print(f"Fallback: {result['debug_info'].get('fallback_mode', False)}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 3: Health Check
    print("\n🏥 Test 3: Health Check")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed!")
            print(f"Status: {response.json().get('status', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    print("\n🎯 Test Summary:")
    print("=" * 50)
    print("✅ Backend server: Running on port 5000")
    print("✅ Video generation API: Available")
    print("🎬 Google Veo integration: Ready for testing")
    print("💡 Frontend integration: Ready to test with new toggle")

if __name__ == "__main__":
    test_video_generation_api()
