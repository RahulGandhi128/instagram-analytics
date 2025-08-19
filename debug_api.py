"""
Quick test to see what data we're getting from the API
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('RAPID_API_KEY') or os.getenv('API_KEY')
headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": "starapi1.p.rapidapi.com",
    "Content-Type": "application/json",
}

url = "https://starapi1.p.rapidapi.com/instagram/user/get_web_profile_info"
payload = {"username": "nasa"}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        json_data = response.json()
        print(f"\\nFull response structure:")
        print(f"Top-level keys: {list(json_data.keys())}")
        
        # Print first few levels to understand structure
        for key, value in json_data.items():
            print(f"\\n'{key}': {type(value)}")
            if isinstance(value, dict):
                print(f"  Sub-keys: {list(value.keys())[:5]}...")  # First 5 keys
            elif isinstance(value, list):
                print(f"  List length: {len(value)}")
            else:
                print(f"  Value preview: {str(value)[:100]}...")
        
        # Save the full response for inspection
        with open('api_response_debug.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"\\n📄 Full response saved to api_response_debug.json")
        
    else:
        print(f"Error {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
