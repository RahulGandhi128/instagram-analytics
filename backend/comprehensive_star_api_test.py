#!/usr/bin/env python3
"""
Comprehensive Star API Test - Test all available endpoints
"""
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://127.0.0.1:5000/api/star-api"
TEST_USERNAME = "nasa"

def test_endpoint(endpoint_name: str, url: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Test a single endpoint and return results"""
    try:
        print(f"\n🔍 Testing {endpoint_name}...")
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        else:
            response = requests.post(url, json=data, timeout=30)
        
        result = {
            'endpoint': endpoint_name,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'url': url
        }
        
        if response.status_code == 200:
            response_data = response.json()
            result['response'] = response_data
            result['data_available'] = response_data.get('success', False)
            print(f"   ✅ {endpoint_name}: SUCCESS")
            if response_data.get('data'):
                data_keys = list(response_data['data'].keys()) if isinstance(response_data['data'], dict) else "non-dict"
                print(f"   📊 Data keys: {data_keys}")
        else:
            print(f"   ❌ {endpoint_name}: FAILED ({response.status_code})")
            try:
                result['error'] = response.json()
            except:
                result['error'] = response.text
        
        return result
        
    except Exception as e:
        print(f"   💥 {endpoint_name}: ERROR - {e}")
        return {
            'endpoint': endpoint_name,
            'status_code': 0,
            'success': False,
            'error': str(e),
            'url': url
        }

def main():
    """Run comprehensive Star API tests"""
    print("🚀 Comprehensive Star API Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Basic User Endpoints
    print("\n📱 BASIC USER ENDPOINTS")
    print("-" * 30)
    
    endpoints = [
        ("User Info", f"{BASE_URL}/user-info/{TEST_USERNAME}"),
        ("User Media", f"{BASE_URL}/user-media/{TEST_USERNAME}?count=5"),
        ("User Stories", f"{BASE_URL}/user-stories/{TEST_USERNAME}"),
        ("User Followers", f"{BASE_URL}/user-followers/{TEST_USERNAME}?count=5"),
        ("User Following", f"{BASE_URL}/user-following/{TEST_USERNAME}?count=5"),
        ("User Highlights", f"{BASE_URL}/user-highlights/{TEST_USERNAME}"),
        ("User Live", f"{BASE_URL}/user-live/{TEST_USERNAME}"),
        ("Similar Accounts", f"{BASE_URL}/user-similar/{TEST_USERNAME}"),
    ]
    
    for name, url in endpoints:
        result = test_endpoint(name, url)
        test_results.append(result)
    
    # Search Endpoints
    print("\n🔍 SEARCH ENDPOINTS")
    print("-" * 20)
    
    search_endpoints = [
        ("Search Users", f"{BASE_URL}/search/users?query=nasa"),
        ("Search Locations", f"{BASE_URL}/search/locations?query=seattle"),
        ("Search Audio", f"{BASE_URL}/search/audio?query=lofi"),
    ]
    
    for name, url in search_endpoints:
        result = test_endpoint(name, url)
        test_results.append(result)
    
    # Location Endpoints (using a sample location ID)
    print("\n📍 LOCATION ENDPOINTS")
    print("-" * 22)
    
    sample_location_id = "108010470985566"  # Sample location ID
    location_endpoints = [
        ("Location Info", f"{BASE_URL}/location/info/{sample_location_id}"),
        ("Location Media", f"{BASE_URL}/location/media/{sample_location_id}?tab=ranked"),
    ]
    
    for name, url in location_endpoints:
        result = test_endpoint(name, url)
        test_results.append(result)
    
    # Hashtag Endpoints
    print("\n#️⃣ HASHTAG ENDPOINTS")
    print("-" * 21)
    
    hashtag_endpoints = [
        ("Hashtag Info", f"{BASE_URL}/hashtag/info/catsofinstagram"),
        ("Hashtag Media", f"{BASE_URL}/hashtag/media/catsofinstagram?tab=top"),
    ]
    
    for name, url in hashtag_endpoints:
        result = test_endpoint(name, url)
        test_results.append(result)
    
    # POST Endpoints
    print("\n📝 POST ENDPOINTS")
    print("-" * 17)
    
    # Highlight Stories (requires highlight IDs)
    highlight_data = {"highlight_ids": ["17902417075637532"]}
    result = test_endpoint("Highlight Stories", f"{BASE_URL}/highlight/stories", "POST", highlight_data)
    test_results.append(result)
    
    # Comment Endpoints (using sample IDs)
    print("\n💬 COMMENT ENDPOINTS")
    print("-" * 20)
    
    sample_comment_id = "18068893951861819"
    sample_media_id = "3582587957616029706"
    
    comment_endpoints = [
        ("Comment Likes", f"{BASE_URL}/comment/likes/{sample_comment_id}"),
        ("Comment Replies", f"{BASE_URL}/comment/replies/{sample_comment_id}?media_id={sample_media_id}"),
    ]
    
    for name, url in comment_endpoints:
        result = test_endpoint(name, url)
        test_results.append(result)
    
    # Audio Endpoints
    print("\n🎵 AUDIO ENDPOINTS")
    print("-" * 17)
    
    sample_audio_id = "2719627934837931"
    result = test_endpoint("Audio Media", f"{BASE_URL}/audio/media/{sample_audio_id}")
    test_results.append(result)
    
    # System Endpoints
    print("\n⚙️ SYSTEM ENDPOINTS")
    print("-" * 18)
    
    system_endpoints = [
        ("Database Status", f"{BASE_URL}/database-status"),
        ("Comprehensive Collection", f"{BASE_URL}/collect-comprehensive/{TEST_USERNAME}"),
    ]
    
    for name, url in system_endpoints:
        method = "POST" if "collect-comprehensive" in url else "GET"
        result = test_endpoint(name, url, method)
        test_results.append(result)
    
    # Test Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in test_results if r['success'])
    total = len(test_results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    print(f"📈 Success Rate: {(successful/total)*100:.1f}%")
    
    # Failed endpoints details
    failed_endpoints = [r for r in test_results if not r['success']]
    if failed_endpoints:
        print("\n❌ FAILED ENDPOINTS:")
        for endpoint in failed_endpoints:
            print(f"   - {endpoint['endpoint']}: {endpoint.get('error', 'Unknown error')}")
    
    # Working endpoints
    working_endpoints = [r for r in test_results if r['success']]
    if working_endpoints:
        print(f"\n✅ WORKING ENDPOINTS ({len(working_endpoints)}):")
        for endpoint in working_endpoints:
            print(f"   - {endpoint['endpoint']}")
    
    print("\n🎉 Comprehensive Star API test completed!")
    
    return test_results

if __name__ == "__main__":
    results = main()
