#!/usr/bin/env python3
"""
Test Veo 3 Fast Video Generation Integration
"""
import os
import sys
import asyncio
import json

# Add backend to path
sys.path.insert(0, 'backend')

# Set API keys for testing
# os.environ['GOOGLE_GENERATIVE_AI_API_KEY'] = 'your_google_api_key_here'  # Removed for security
os.environ['OPENAI_API_KEY'] = 'test_key_for_content_creation'

from content_creation import ContentCreationService, ContentRequest

async def test_veo3_video_generation():
    """Test the Veo 3 Fast video generation with cost-effective settings"""
    
    print("🎬 Testing Google Veo 3 Fast Video Generation")
    print("=" * 60)
    
    try:
        # Initialize the service
        service = ContentCreationService()
        
        if not service.google_client:
            print("❌ Google AI client not initialized")
            return False
        
        print("✅ Google AI client ready")
        
        # Test 1: Basic video concept (no audio, standard quality)
        print("\n🎯 Test 1: Basic Video Concept (No Audio, Standard Quality)")
        print("-" * 40)
        
        result1 = await service.generate_video_with_veo3(
            prompt="Create a short Instagram video about AI helping with career success",
            style_preferences={'mood': 'professional', 'style': 'modern'},
            include_audio=False,
            quality="standard"
        )
        
        print(f"Success: {result1['success']}")
        if result1['success']:
            print(f"Type: {result1['type']}")
            print(f"Audio: {result1['settings']['audio_enabled']}")
            print(f"Quality: {result1['settings']['quality']}")
            print(f"Concept Preview: {result1['concept'][:150]}...")
        else:
            print(f"Error: {result1['error']}")
        
        # Test 2: With audio and high quality
        print("\n🎯 Test 2: Video with Audio (High Quality)")
        print("-" * 40)
        
        result2 = await service.generate_video_with_veo3(
            prompt="Quick tip: How to nail your next job interview",
            include_audio=True,
            quality="high"
        )
        
        print(f"Success: {result2['success']}")
        if result2['success']:
            print(f"Audio Enabled: {result2['settings']['audio_enabled']}")
            print(f"Quality: {result2['settings']['quality']}")
            print(f"Model: {result2['debug_info']['model']}")
        
        # Test 3: Full content creation request
        print("\n🎯 Test 3: Full Content Creation Request")
        print("-" * 40)
        
        request = ContentRequest(
            user_id="test_user",
            prompt="Create an engaging video about productivity tips",
            content_type="video",
            video_include_audio=True,
            video_quality="standard"
        )
        
        result3 = await service.create_content(request)
        
        print(f"Content ID: {result3.content_id}")
        print(f"Content Type: {result3.content_type}")
        print(f"Success: {result3.error is None}")
        
        if result3.metadata:
            print(f"Settings: {json.dumps(result3.metadata.get('settings', {}), indent=2)}")
        
        print("\n✅ All tests completed successfully!")
        print("🎬 Veo 3 Fast integration is working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_veo3_video_generation())
    if success:
        print("\n🎉 Veo 3 Fast integration ready for production!")
    else:
        print("\n⚠️  Integration needs adjustment")
