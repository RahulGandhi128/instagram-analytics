"""
Quick Test Script for Star API
Simple script to test basic functionality
"""
import requests
import json

def quick_test():
    """Quick test of Star API functionality"""
    base_url = "http://localhost:5000/api"
    test_username = "instagram"
    
    print("🚀 Quick Star API Test")
    print("=" * 30)
    
    # Test 1: Check if backend is running
    try:
        response = requests.get(f"{base_url}/analytics/summary-stats", timeout=5)
        print("✅ Backend is running")
    except:
        print("❌ Backend is not running. Start it with: cd backend && python app.py")
        return False
    
    # Test 2: Check database status
    try:
        response = requests.get(f"{base_url}/star-api/database-status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                db_data = data.get('data', {})
                print(f"✅ Database connected - Profiles: {db_data.get('profiles', 0)}")
            else:
                print(f"⚠️  Database issue: {data.get('error', 'Unknown')}")
        else:
            print(f"❌ Database status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    
    # Test 3: Test basic user info endpoint
    try:
        response = requests.get(f"{base_url}/star-api/user-info/{test_username}", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ User info API working - Got data for {test_username}")
            else:
                print(f"⚠️  User info API issue: {data.get('error', 'Unknown')}")
        else:
            print(f"❌ User info test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User info test failed: {e}")
    
    # Test 4: Test endpoint testing functionality
    try:
        response = requests.post(
            f"{base_url}/star-api/test-endpoints",
            json={"username": test_username},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                test_data = data.get('data', {})
                endpoint_results = test_data.get('endpoint_results', {})
                successful_endpoints = sum(1 for r in endpoint_results.values() if r.get('status') == 'success')
                total_endpoints = len(endpoint_results)
                print(f"✅ Endpoint testing working - {successful_endpoints}/{total_endpoints} endpoints successful")
            else:
                print(f"⚠️  Endpoint testing issue: {data.get('error', 'Unknown')}")
        else:
            print(f"❌ Endpoint testing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Endpoint testing failed: {e}")
    
    print("\\n" + "=" * 30)
    print("Quick test completed!")
    print("\\nFor comprehensive testing, run:")
    print("python test_star_api.py")
    
    return True

if __name__ == "__main__":
    quick_test()
