import sqlite3

conn = sqlite3.connect('instagram_analytics.db')
cursor = conn.cursor()

# Check the structure of the media table
cursor.execute("PRAGMA table_info(media)")
columns = cursor.fetchall()
print("Current media table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check what the API expects vs what we have
api_expected_fields = [
    'save_count', 'share_count', 'hashtags', 'mentions', 'shortcode',
    'video_view_count', 'location_name', 'location_id', 'is_ad', 'is_sponsored',
    'data_quality_score'
]

print(f"\nMissing fields that API expects:")
current_columns = [col[1] for col in columns]
for field in api_expected_fields:
    if field not in current_columns:
        print(f"  - {field}")

# Check NASA data
cursor.execute("SELECT COUNT(*) FROM media WHERE username = 'nasa'")
count = cursor.fetchone()[0]
print(f"\nNASA posts in database: {count}")

if count > 0:
    cursor.execute("SELECT id, like_count, comment_count FROM media WHERE username = 'nasa' LIMIT 3")
    posts = cursor.fetchall()
    print("Sample posts:")
    for post in posts:
        print(f"  - {post[0]}: {post[1]} likes, {post[2]} comments")

conn.close()
