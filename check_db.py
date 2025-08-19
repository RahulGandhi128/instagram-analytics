import sqlite3
import json

# Connect to the database
conn = sqlite3.connect('instagram_analytics.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', [table[0] for table in tables])

# Check profiles
try:
    cursor.execute("SELECT username, full_name, follower_count, following_count, post_count FROM profiles")
    profiles = cursor.fetchall()
    print(f'\nProfiles ({len(profiles)}):')
    for profile in profiles:
        print(f'- {profile[0]} ({profile[1]}): {profile[2]} followers, {profile[3]} following, {profile[4]} posts')
except Exception as e:
    print(f"Error getting profiles: {e}")

# Check media posts count
try:
    cursor.execute("SELECT COUNT(*) FROM media_posts WHERE username = 'nasa'")
    nasa_posts_count = cursor.fetchone()[0]
    print(f'\nNASA media posts: {nasa_posts_count}')
except Exception as e:
    print(f"Error counting NASA posts: {e}")

# Check some sample posts
try:
    cursor.execute("SELECT id, caption, like_count, comment_count, post_datetime_ist FROM media_posts WHERE username = 'nasa' LIMIT 5")
    posts = cursor.fetchall()
    print('\nSample NASA posts:')
    for post in posts:
        print(f'- {post[0]}: {post[2]} likes, {post[3]} comments')
        caption = post[1][:50] if post[1] else 'No caption'
        print(f'  Caption: {caption}...')
        print(f'  Date: {post[4]}')
except Exception as e:
    print(f"Error getting posts: {e}")

# Check if we have any real data (not sample_1, sample_2, sample_3)
try:
    cursor.execute("SELECT COUNT(*) FROM media_posts WHERE username = 'nasa' AND id NOT LIKE 'sample_%'")
    real_posts_count = cursor.fetchone()[0]
    print(f'\nReal NASA posts (not samples): {real_posts_count}')
    
    if real_posts_count > 0:
        cursor.execute("SELECT id, like_count, comment_count FROM media_posts WHERE username = 'nasa' AND id NOT LIKE 'sample_%' LIMIT 3")
        real_posts = cursor.fetchall()
        print('Sample real posts:')
        for post in real_posts:
            print(f'- {post[0]}: {post[1]} likes, {post[2]} comments')
except Exception as e:
    print(f"Error getting real posts: {e}")

conn.close()
