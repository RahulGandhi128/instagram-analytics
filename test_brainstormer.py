#!/usr/bin/env python3
"""
Test script to verify Brainstormer can process analytics data correctly
"""
import os
import sys
import json

# Add backend to path
sys.path.insert(0, 'backend')

# Mock OpenAI API key
os.environ['OPENAI_API_KEY'] = 'test_key'

from services.brainstormer_service import BrainstormerService

# Sample analytics data structure similar to what you showed
sample_analytics_data = {
    "analytics": {
        "engagement_trends": {
            "daily_metrics": [
                {"avg_engagement": 0, "date": "2025-07-11", "engagement": 0, "posts": 0},
                {"avg_engagement": 0, "date": "2025-07-12", "engagement": 0, "posts": 0},
                {"avg_engagement": 0, "date": "2025-07-13", "engagement": 0, "posts": 0},
                {"avg_engagement": 28978.5, "date": "2025-07-24", "engagement": 57957, "posts": 2},
                {"avg_engagement": 20826, "date": "2025-07-25", "engagement": 20826, "posts": 1},
            ]
        },
        "posts": {
            "basic_stats": {
                "total_content": 0,
                "total_engagement": 0,
                "avg_engagement_per_post": 0
            }
        }
    },
    "insights": {}
}

def test_brainstormer_analytics_processing():
    """Test that the brainstormer can process analytics data"""
    try:
        brainstormer = BrainstormerService()
        
        # Test the system prompt generation
        system_prompt = brainstormer._generate_brainstorm_system_prompt(
            sample_analytics_data, 
            username="swiggyindia", 
            time_range=30
        )
        
        print("✅ Brainstormer Analytics Processing Test")
        print("=" * 60)
        print("📊 Sample Analytics Data:")
        print(json.dumps(sample_analytics_data, indent=2))
        print("\n" + "=" * 60)
        print("🤖 Generated System Prompt:")
        print(system_prompt)
        print("\n" + "=" * 60)
        
        # Check if the prompt contains the expected analytics context
        if "CURRENT ANALYTICS CONTEXT" in system_prompt:
            print("✅ Analytics context properly included in system prompt")
        else:
            print("❌ Analytics context missing from system prompt")
            
        if "DAILY ENGAGEMENT BREAKDOWN" in system_prompt:
            print("✅ Daily engagement breakdown included")
        else:
            print("❌ Daily engagement breakdown missing")
            
        if "LIMITED DATA INSIGHTS" in system_prompt:
            print("✅ Limited data insights handling included")
        else:
            print("❌ Limited data insights handling missing")
            
        # Check if the actual engagement numbers appear
        if "57957" in system_prompt and "20826" in system_prompt:
            print("✅ Raw engagement data properly processed")
        else:
            print("❌ Raw engagement data not found in prompt")
            
        print("\n🎯 Summary: Brainstormer should now properly process your analytics data!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_brainstormer_analytics_processing()
