"""
Single Account Test - Focus on ONE account
Test NASA account step by step
"""
import requests
import json

def test_single_account():
    """Test a single account (NASA) step by step"""
    base_url = "http://localhost:5000/api"
    username = "nasa"  # Public account, should work
    
    print(f"🧪 Testing Single Account: {username}")
    print("=" * 50)
    
    # Step 1: Test user info
    print("\\n🔍 Step 1: Testing User Info...")
    try:
        response = requests.get(f"{base_url}/star-api/user-info/{username}", timeout=15)
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response Keys: {list(data.keys())}")
            
            if data.get('success'):
                # Debug: Print the actual structure
                print(f"   Response Structure: {json.dumps(data, indent=2)[:300]}...")
                
                # Try to extract user data with proper error handling
                try:
                    user_data = data['data']['response']['body']['data']['user']
                    user_id = user_data['id']
                    print(f"   ✅ User Info: {user_data['username']} (ID: {user_id})")
                    print(f"   📊 Followers: {user_data.get('follower_count', 'N/A')}")
                    print(f"   📝 Bio: {user_data.get('biography', 'N/A')[:50]}...")
                except KeyError as ke:
                    print(f"   ❌ Key Error: {ke}")
                    print(f"   📋 Available keys in data: {list(data.get('data', {}).keys())}")
                    return False
            else:
                print(f"   ❌ User Info Error: {data.get('error')}")
                return False
        else:
            print(f"   ❌ User Info Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"   ❌ User Info Exception: {e}")
        return False
    
    # Step 2: Test user media
    print("\\n📸 Step 2: Testing User Media...")
    try:
        response = requests.get(f"{base_url}/star-api/user-media/{username}?count=5", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Media API working!")
                # Try to count media items
                try:
                    media_items = data['data']['response']['body']['data']['user']['media']['edges']
                    print(f"   📊 Media count: {len(media_items)}")
                    if media_items:
                        first_media = media_items[0]['node']
                        print(f"   🎯 Sample media: {first_media.get('shortcode', 'N/A')}")
                except:
                    print(f"   ⚠️  Media data structure different than expected")
                    print(f"   📋 Media response keys: {list(data.get('data', {}).keys())}")
            else:
                print(f"   ❌ Media Error: {data.get('error')}")
        else:
            print(f"   ❌ Media Failed: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Media Exception: {e}")
    
    # Step 3: Test user stories
    print("\\n📱 Step 3: Testing User Stories...")
    try:
        response = requests.get(f"{base_url}/star-api/user-stories/{username}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Stories API working!")
                try:
                    # Try to count stories
                    print(f"   📊 Stories response received")
                except:
                    print(f"   ⚠️  Stories data structure different than expected")
            else:
                print(f"   ❌ Stories Error: {data.get('error')}")
        else:
            print(f"   ❌ Stories Failed: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Stories Exception: {e}")
    
    # Step 4: Test comprehensive collection
    print("\\n🔄 Step 4: Testing Comprehensive Collection...")
    try:
        response = requests.post(f"{base_url}/star-api/collect-comprehensive/{username}", timeout=60)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                collection_data = data.get('data', {})
                collected = collection_data.get('data_collected', {})
                errors = collection_data.get('errors', [])
                print(f"   ✅ Comprehensive collection working!")
                print(f"   📊 Data collected: {list(collected.keys())}")
                if errors:
                    print(f"   ⚠️  Errors: {len(errors)}")
                    for error in errors[:3]:  # Show first 3 errors
                        print(f"      - {error}")
            else:
                print(f"   ❌ Collection Error: {data.get('error')}")
        else:
            print(f"   ❌ Collection Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Collection Exception: {e}")

    # Step 5: Test new endpoints
    print("\\n🔗 Step 5: Testing New Endpoints...")
    
    # Test followers
    print("   👥 Testing Followers...")
    try:
        response = requests.get(f"{base_url}/star-api/user-followers/{username}?count=5", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Followers API working!")
            else:
                print(f"   ❌ Followers Error: {data.get('error')}")
        else:
            print(f"   ❌ Followers Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Followers Exception: {e}")
    
    # Test following
    print("   👤 Testing Following...")
    try:
        response = requests.get(f"{base_url}/star-api/user-following/{username}?count=5", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Following API working!")
            else:
                print(f"   ❌ Following Error: {data.get('error')}")
        else:
            print(f"   ❌ Following Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Following Exception: {e}")
    
    # Test highlights
    print("   ⭐ Testing Highlights...")
    try:
        response = requests.get(f"{base_url}/star-api/user-highlights/{username}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Highlights API working!")
            else:
                print(f"   ❌ Highlights Error: {data.get('error')}")
        else:
            print(f"   ❌ Highlights Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Highlights Exception: {e}")
    
    # Test live
    print("   🔴 Testing Live...")
    try:
        response = requests.get(f"{base_url}/star-api/user-live/{username}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Live API working!")
            else:
                print(f"   ❌ Live Error: {data.get('error')}")
        else:
            print(f"   ❌ Live Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Live Exception: {e}")
    
    print("\\n" + "=" * 50)
    print("Single account test completed!")
    
    return True

if __name__ == "__main__":
    test_single_account()
