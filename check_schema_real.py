import sqlite3

# Check the actual database schema vs what the models expect
conn = sqlite3.connect('instagram_analytics.db')
cursor = conn.cursor()

print("=== PROFILES TABLE ===")
cursor.execute("PRAGMA table_info(profiles)")
profiles_cols = cursor.fetchall()
for col in profiles_cols:
    print(f"  {col[1]} ({col[2]})")

print(f"\n=== MEDIA TABLE ===")
cursor.execute("PRAGMA table_info(media)")
media_cols = cursor.fetchall()
for col in media_cols:
    print(f"  {col[1]} ({col[2]})")

# Try to manually fetch NASA data
print(f"\n=== NASA DATA TEST ===")
cursor.execute("SELECT username, full_name FROM profiles WHERE username = 'nasa'")
nasa_profile = cursor.fetchone()
if nasa_profile:
    print(f"NASA Profile found: {nasa_profile[1]}")
else:
    print("NASA Profile not found!")

cursor.execute("SELECT id, like_count, comment_count FROM media WHERE username = 'nasa' LIMIT 3")
nasa_posts = cursor.fetchall()
print(f"NASA posts found: {len(nasa_posts)}")
for post in nasa_posts:
    print(f"  - {post[0]}: {post[1]} likes, {post[2]} comments")

conn.close()
