import requests

# Check what profiles are available
try:
    response = requests.get('http://localhost:5000/api/profiles', timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        profiles = data.get('data', [])
        
        print(f"Available profiles ({len(profiles)}):")
        for profile in profiles:
            print(f"- {profile.get('username')}: {profile.get('full_name')} ({profile.get('follower_count', 0):,} followers)")
    else:
        print(f"Error: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
