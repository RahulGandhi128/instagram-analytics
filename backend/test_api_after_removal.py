#!/usr/bin/env python3
"""
Test API functionality after removing Google API key
- Text/Image generation should work with OpenAI
- Video generation should show proper error
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_text_generation():
    """Test that text generation still works with OpenAI"""
    print("🔤 Testing Text Generation (OpenAI)...")
    
    payload = {
        "user_id": "test_user",
        "prompt": "Write a short Instagram caption about productivity",
        "content_type": "text",
        "style_preferences": {
            "tone": "professional",
            "length": "short"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/content/create", json=payload, timeout=30)
        result = response.json()
        
        if result.get('success'):
            print("✅ Text generation working! OpenAI is functioning correctly")
            print(f"   Content: {result.get('content', '')[:100]}...")
            return True
        else:
            print(f"❌ Text generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_image_generation():
    """Test that image generation still works with OpenAI DALL-E"""
    print("\n🖼️ Testing Image Generation (DALL-E)...")
    
    payload = {
        "user_id": "test_user", 
        "prompt": "A simple modern logo for a tech startup",
        "content_type": "image",
        "style_preferences": {
            "style": "minimalist",
            "color_scheme": "blue and white"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/content/create", json=payload, timeout=45)
        result = response.json()
        
        if result.get('success') and result.get('content_url'):
            print("✅ Image generation working! DALL-E is functioning correctly")
            print(f"   Image URL: {result.get('content_url', '')[:80]}...")
            return True
        else:
            print(f"❌ Image generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_video_generation_error():
    """Test that video generation shows proper error without Google API key"""
    print("\n🎬 Testing Video Generation (Should show error)...")
    
    payload = {
        "user_id": "test_user",
        "prompt": "Create a short video about career tips",
        "content_type": "video",
        "video_include_audio": False,
        "video_quality": "standard",
        "video_generate_actual": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/content/create", json=payload, timeout=30)
        result = response.json()
        
        if not result.get('success') and 'Google Generative AI API key is required' in result.get('error', ''):
            print("✅ Video generation correctly shows API key error!")
            print(f"   Error message: {result.get('error', '')}")
            return True
        elif result.get('success'):
            print("❌ Video generation should not work without Google API key")
            return False
        else:
            print(f"❓ Unexpected error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_health_check():
    """Test basic health check"""
    print("\n🏥 Testing Health Check...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        result = response.json()
        
        if response.status_code == 200:
            print("✅ Backend health check passed!")
            return True
        else:
            print(f"❌ Health check failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Health check request failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing API Functionality After Google API Key Removal")
    print("=" * 65)
    
    # Give server a moment to fully restart
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        test_health_check,
        test_text_generation, 
        test_image_generation,
        test_video_generation_error
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API working correctly:")
        print("   ✅ OpenAI models (text/image) functional")
        print("   ✅ Video generation properly disabled") 
        print("   ✅ Google API key safely removed")
    else:
        print("⚠️ Some tests failed - check logs above")
    
    return passed == total

if __name__ == "__main__":
    main()
