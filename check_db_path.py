import sqlite3
import os

# Check what database the Flask app is using
backend_dir = r"c:\Users\parth\mentra project\backend"
parent_dir = r"c:\Users\parth\mentra project"

db_path_from_backend = os.path.join(parent_dir, "instagram_analytics.db")
print(f"Expected database path: {db_path_from_backend}")
print(f"File exists: {os.path.exists(db_path_from_backend)}")

if os.path.exists(db_path_from_backend):
    print(f"File size: {os.path.getsize(db_path_from_backend)} bytes")
    
    # Check content
    conn = sqlite3.connect(db_path_from_backend)
    cursor = conn.cursor()
    
    # Check profiles
    cursor.execute("SELECT COUNT(*) FROM profiles")
    profile_count = cursor.fetchone()[0]
    print(f"Profiles in database: {profile_count}")
    
    if profile_count > 0:
        cursor.execute("SELECT username, full_name FROM profiles")
        profiles = cursor.fetchall()
        print("Profiles:")
        for profile in profiles:
            print(f"  - {profile[0]}: {profile[1]}")
    
    # Check media
    cursor.execute("SELECT COUNT(*) FROM media WHERE username = 'nasa'")
    nasa_count = cursor.fetchone()[0]
    print(f"NASA media posts: {nasa_count}")
    
    conn.close()
else:
    print("Database file not found!")
