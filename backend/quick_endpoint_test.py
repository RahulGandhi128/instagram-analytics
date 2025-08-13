#!/usr/bin/env python3
"""
Quick test for specific failing endpoints
"""
import requests
import time

def test_endpoint(name, url):
    try:
        print(f"Testing {name}: {url}")
        response = requests.get(url, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', 'N/A')}")
        else:
            print(f"  Error: {response.text}")
        print()
    except Exception as e:
        print(f"  Exception: {e}")
        print()

if __name__ == "__main__":
    base_url = "http://127.0.0.1:5000/api/star-api"
    
    print("Testing specific failing endpoints...")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Test endpoints that are failing
    test_endpoint("User Similar", f"{base_url}/user-similar/nasa")
    test_endpoint("Search Users", f"{base_url}/search/users?query=nasa")
    test_endpoint("Search Locations", f"{base_url}/search/locations?query=seattle")
    test_endpoint("Location Info", f"{base_url}/location/info/108010470985566")
    test_endpoint("Hashtag Info", f"{base_url}/hashtag/info/catsofinstagram")
