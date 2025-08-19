import sqlite3

# Connect to the database
conn = sqlite3.connect('instagram_analytics.db')
cursor = conn.cursor()

# Check table schemas
tables = ['profiles', 'media', 'stories']

for table in tables:
    print(f"\n=== {table.upper()} TABLE ===")
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print("Columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Total rows: {count}")
        
        if table == 'profiles':
            cursor.execute("SELECT username, full_name, follower_count, following_count FROM profiles")
            profiles = cursor.fetchall()
            print("Profiles:")
            for profile in profiles:
                print(f"  - {profile[0]} ({profile[1]}): {profile[2]} followers, {profile[3]} following")
        
        elif table == 'media' and count > 0:
            cursor.execute("SELECT COUNT(*) FROM media WHERE username = 'nasa'")
            nasa_count = cursor.fetchone()[0]
            print(f"NASA posts: {nasa_count}")
            
            if nasa_count > 0:
                cursor.execute("SELECT id, like_count, comment_count, caption FROM media WHERE username = 'nasa' LIMIT 3")
                posts = cursor.fetchall()
                print("Sample NASA posts:")
                for post in posts:
                    caption = post[3][:50] if post[3] else 'No caption'
                    print(f"  - {post[0]}: {post[1]} likes, {post[2]} comments")
                    print(f"    Caption: {caption}...")
                    
    except Exception as e:
        print(f"Error with {table}: {e}")

conn.close()
