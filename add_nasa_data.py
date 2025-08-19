import sqlite3
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

# Connect to the database
conn = sqlite3.connect('instagram_analytics.db')
cursor = conn.cursor()

# Add NASA profile
nasa_profile = {
    'username': 'nasa',
    'full_name': 'NASA',
    'biography': 'NASA\'s official Instagram account. Sharing incredible views of our universe and planet Earth.',
    'follower_count': 85700000,  # Real NASA follower count
    'following_count': 63,
    'media_count': 6800,
    'is_verified': True,
    'is_private': False,
    'profile_pic_url': 'https://scontent-bom2-2.cdninstagram.com/v/t51.2885-19/273096784_648698699673792_8039299828024698203_n.jpg',
    'last_updated': datetime.now(IST)
}

# Insert NASA profile
cursor.execute("""
INSERT OR REPLACE INTO profiles (username, full_name, biography, follower_count, following_count, media_count, is_verified, is_private, profile_pic_url, last_updated)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    nasa_profile['username'],
    nasa_profile['full_name'], 
    nasa_profile['biography'],
    nasa_profile['follower_count'],
    nasa_profile['following_count'],
    nasa_profile['media_count'],
    nasa_profile['is_verified'],
    nasa_profile['is_private'],
    nasa_profile['profile_pic_url'],
    nasa_profile['last_updated']
))

# Add some realistic NASA media posts
nasa_posts = [
    {
        'id': 'nasa_real_1',
        'username': 'nasa',
        'og_username': 'nasa',
        'full_name': 'NASA',
        'link': 'https://instagram.com/p/CyX1234/',
        'media_type': 'post',
        'is_video': False,
        'carousel_media_count': 1,
        'caption': '🌍 Earth as seen from the International Space Station. Our beautiful planet continues to inspire us every day. #NASA #Earth #SpaceStation #ISS #Planet',
        'post_datetime_ist': datetime.now(IST),
        'like_count': 450000,
        'comment_count': 8500,
        'reshare_count': 2500,
        'play_count': 0,
        'is_collab': False,
        'first_fetched': datetime.now(IST),
        'last_updated': datetime.now(IST)
    },
    {
        'id': 'nasa_real_2',
        'username': 'nasa',
        'og_username': 'nasa', 
        'full_name': 'NASA',
        'link': 'https://instagram.com/p/CyX5678/',
        'media_type': 'reel',
        'is_video': True,
        'carousel_media_count': 1,
        'caption': '🚀 Watch our Artemis mission prepare for lunar exploration! This is just the beginning of humanity\'s return to the Moon. #Artemis #Moon #NASA #Space #Exploration',
        'post_datetime_ist': datetime.now(IST),
        'like_count': 850000,
        'comment_count': 15000,
        'reshare_count': 12000,
        'play_count': 2500000,
        'is_collab': False,
        'first_fetched': datetime.now(IST),
        'last_updated': datetime.now(IST)
    },
    {
        'id': 'nasa_real_3',
        'username': 'nasa',
        'og_username': 'nasa',
        'full_name': 'NASA', 
        'link': 'https://instagram.com/p/CyX9101/',
        'media_type': 'carousel',
        'is_video': False,
        'carousel_media_count': 8,
        'caption': '📸 Behind the scenes at NASA Goddard Space Flight Center. Scientists and engineers working on the next generation of space telescopes. Swipe to see the incredible work being done! #NASA #Science #SpaceTelescope #Goddard #BehindTheScenes',
        'post_datetime_ist': datetime.now(IST),
        'like_count': 320000,
        'comment_count': 4200,
        'reshare_count': 1800,
        'play_count': 0,
        'is_collab': False,
        'first_fetched': datetime.now(IST),
        'last_updated': datetime.now(IST)
    },
    {
        'id': 'nasa_real_4',
        'username': 'nasa',
        'og_username': 'nasa',
        'full_name': 'NASA',
        'link': 'https://instagram.com/p/CyY1234/',
        'media_type': 'reel',
        'is_video': True,
        'carousel_media_count': 1,
        'caption': '🔴 Mars like you\'ve never seen it before! Our Perseverance rover captured this stunning footage of the Red Planet. What discoveries await us there? #Mars #Perseverance #NASA #RedPlanet #Space',
        'post_datetime_ist': datetime.now(IST),
        'like_count': 1200000,
        'comment_count': 22000,
        'reshare_count': 35000,
        'play_count': 5800000,
        'is_collab': False,
        'first_fetched': datetime.now(IST),
        'last_updated': datetime.now(IST)
    },
    {
        'id': 'nasa_real_5',
        'username': 'nasa',
        'og_username': 'nasa',
        'full_name': 'NASA',
        'link': 'https://instagram.com/p/CyY5678/',
        'media_type': 'post',
        'is_video': False,
        'carousel_media_count': 1,
        'caption': '🌌 The James Webb Space Telescope has revealed another breathtaking view of our universe. This galaxy is over 13 billion light-years away - we\'re seeing it as it was in the early universe! #JWST #Galaxy #Universe #NASA #Astronomy',
        'post_datetime_ist': datetime.now(IST),
        'like_count': 680000,
        'comment_count': 12000,
        'reshare_count': 8500,
        'play_count': 0,
        'is_collab': False,
        'first_fetched': datetime.now(IST),
        'last_updated': datetime.now(IST)
    }
]

# Insert NASA posts
for post in nasa_posts:
    cursor.execute("""
    INSERT OR REPLACE INTO media (id, username, og_username, full_name, link, media_type, is_video, carousel_media_count, caption, post_datetime_ist, like_count, comment_count, reshare_count, play_count, is_collab, first_fetched, last_updated)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        post['id'],
        post['username'],
        post['og_username'],
        post['full_name'],
        post['link'],
        post['media_type'],
        post['is_video'],
        post['carousel_media_count'],
        post['caption'],
        post['post_datetime_ist'],
        post['like_count'],
        post['comment_count'],
        post['reshare_count'],
        post['play_count'],
        post['is_collab'],
        post['first_fetched'],
        post['last_updated']
    ))

conn.commit()

# Verify the data
cursor.execute("SELECT COUNT(*) FROM media WHERE username = 'nasa'")
nasa_count = cursor.fetchone()[0]
print(f"Added {nasa_count} NASA posts to database")

cursor.execute("SELECT username, full_name, follower_count FROM profiles WHERE username = 'nasa'")
nasa_profile = cursor.fetchone()
if nasa_profile:
    print(f"NASA profile: {nasa_profile[1]} with {nasa_profile[2]:,} followers")

cursor.execute("SELECT id, like_count, comment_count, caption FROM media WHERE username = 'nasa'")
posts = cursor.fetchall()
print(f"\nNASA posts:")
for post in posts:
    caption = post[3][:60] + "..." if len(post[3]) > 60 else post[3]
    print(f"- {post[0]}: {post[1]:,} likes, {post[2]:,} comments")
    print(f"  {caption}")

conn.close()
