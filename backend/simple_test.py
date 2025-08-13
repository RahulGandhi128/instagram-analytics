"""
Quick Fix Test for Star API
Tests with different usernames and simpler approach
"""
import requests
import json

def test_star_api_simple():
    """Simple test to verify Star API is working"""
    base_url = "http://localhost:5000/api"
    
    print("🔧 Star API Simple Test")
    print("=" * 30)
    
    # Test with different usernames that are likely to work
    test_usernames = ["nasa", "natgeo", "cristiano"]  # Public, popular accounts
    
    for username in test_usernames:
        print(f"\\nTesting with username: {username}")
        
        try:
            # Test user info endpoint
            response = requests.get(f"{base_url}/star-api/user-info/{username}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"  ✅ User info API working for {username}")
                    
                    # Quick test of comprehensive collection
                    try:
                        response = requests.post(
                            f"{base_url}/star-api/collect-comprehensive/{username}",
                            timeout=30
                        )
                        if response.status_code == 200:
                            result = response.json()
                            if result.get('success'):
                                collected = result.get('data', {}).get('data_collected', {})
                                print(f"  ✅ Data collection working - collected: {list(collected.keys())}")
                                break  # If one works, that's good enough
                            else:
                                print(f"  ⚠️  Collection issue: {result.get('error')}")
                        else:
                            print(f"  ❌ Collection failed: {response.status_code}")
                    except Exception as e:
                        print(f"  ❌ Collection test failed: {e}")
                else:
                    print(f"  ⚠️  User info API issue: {data.get('error')}")
            else:
                print(f"  ❌ User info failed: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
    
    # Test database status
    try:
        response = requests.get(f"{base_url}/star-api/database-status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                db_data = data.get('data', {})
                print(f"\\n✅ Database working - Profiles: {db_data.get('profiles', 0)}")
            else:
                print(f"\\n❌ Database issue: {data.get('error')}")
        else:
            print(f"\\n❌ Database status failed: {response.status_code}")
    except Exception as e:
        print(f"\\n❌ Database test failed: {e}")
    
    print("\\n" + "=" * 30)
    print("Simple test completed!")

if __name__ == "__main__":
    test_star_api_simple()
