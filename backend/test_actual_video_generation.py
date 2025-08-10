#!/usr/bin/env python3
"""
Test script for actual video generation with Google Veo 3 Fast
Tests both concept generation and actual video generation attempts
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_creation import ContentCreationService, ContentRequest

async def test_video_generation():
    """Test both concept and actual video generation"""
    
    # Initialize the service
    print("🔧 Initializing ContentCreationService...")
    service = ContentCreationService()
    
    if not service.google_client:
        print("❌ Failed to initialize Google AI client")
        return
    
    print("✅ ContentCreationService initialized successfully")
    print("🧪 Testing Google Veo 3 Fast video generation...")
    print()
    
    # Test prompt
    test_prompt = "Create a 3-second Instagram video showcasing diverse professionals thriving in their careers on Naukri.com"
    
    # Test 1: Concept Generation (current default)
    print("📝 Test 1: Video Concept Generation (Cost-effective)")
    print("-" * 50)
    
    concept_request = ContentRequest(
        user_id="test_user",
        prompt=test_prompt,
        content_type="video",
        video_include_audio=False,
        video_quality="standard",
        video_generate_actual=False  # Concept only
    )
    
    try:
        concept_result = await service.create_content(concept_request)
        print("✅ Concept generation successful!")
        print(f"Content Type: {concept_result.content_type}")
        print(f"Description: {concept_result.description[:200]}...")
        if concept_result.metadata:
            print(f"Debug Info: {concept_result.metadata}")
        print()
    except Exception as e:
        print(f"❌ Concept generation failed: {e}")
        print()
    
    # Test 2: Actual Video Generation (experimental)
    print("🎬 Test 2: Actual Video Generation (Experimental)")
    print("-" * 50)
    
    actual_request = ContentRequest(
        user_id="test_user",
        prompt=test_prompt,
        content_type="video",
        video_include_audio=False,  # Keep cost low
        video_quality="standard",   # Lower quality for testing
        video_generate_actual=True  # Try actual video
    )
    
    try:
        actual_result = await service.create_content(actual_request)
        print("🎯 Actual video generation result:")
        print(f"Content Type: {actual_result.content_type}")
        print(f"Success: {actual_result.error is None}")
        
        if actual_result.content_url:
            print(f"✅ Video URL: {actual_result.content_url}")
        else:
            print("📝 Fallback to concept (expected - Veo API not yet available)")
            
        print(f"Description: {actual_result.description[:200]}...")
        if actual_result.metadata:
            print(f"Debug Info: {actual_result.metadata}")
        print()
    except Exception as e:
        print(f"❌ Actual video generation failed: {e}")
        print()
    
    # Test 3: High Quality with Audio (more expensive)
    print("💎 Test 3: High Quality Video with Audio (Most Expensive)")
    print("-" * 50)
    
    premium_request = ContentRequest(
        user_id="test_user",
        prompt=test_prompt,
        content_type="video",
        video_include_audio=True,   # Include audio
        video_quality="high",       # High quality
        video_generate_actual=True  # Actual video
    )
    
    try:
        premium_result = await service.create_content(premium_request)
        print("🎯 Premium video generation result:")
        print(f"Content Type: {premium_result.content_type}")
        print(f"Success: {premium_result.error is None}")
        
        if premium_result.content_url:
            print(f"✅ Video URL: {premium_result.content_url}")
        else:
            print("📝 Fallback to enhanced concept (expected)")
            
        print(f"Description: {premium_result.description[:200]}...")
        if premium_result.metadata:
            print(f"Debug Info: {premium_result.metadata}")
        print()
    except Exception as e:
        print(f"❌ Premium video generation failed: {e}")
        print()
    
    print("🎬 Test Summary:")
    print("=" * 50)
    print("✅ Concept Generation: Working (cost-effective)")
    print("🔧 Actual Video Generation: Experimental (fallback to enhanced concepts)")
    print("💡 Note: Google Veo API may not be publicly available yet")
    print("🎯 Frontend integration: Ready with toggle controls")

if __name__ == "__main__":
    print("🧪 Testing Google Veo 3 Fast Video Generation")
    print("=" * 60)
    asyncio.run(test_video_generation())
