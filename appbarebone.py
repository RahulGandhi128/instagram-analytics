"""
Instagram Social Media Analytics MVP
Fetches and analyzes Instagram data for performance insights
"""

import requests
import pandas as pd
import datetime
import pytz
import sqlite3
import os
from typing import Dict, List, Optional
import json
import time

# Configuration
USERNAMES = ["naukridotcom", "swiggyindia", "zomato", "instagram"]
API_KEY = "55325f396cmsh1812ff7f2016376p1079d8jsn5ef3a673c06c"

# API Endpoints
URL_PROFILE = "https://starapi1.p.rapidapi.com/instagram/user/get_web_profile_info"
URL_MEDIA = "https://starapi1.p.rapidapi.com/instagram/user/get_media"
URL_STORIES = "https://starapi1.p.rapidapi.com/instagram/user/get_stories"

# Timezone setup
IST = pytz.timezone("Asia/Kolkata")

# Media type mappings
MEDIA_TYPE_MAP = {1: "post", 2: "reel", 8: "carousel"}
STORY_TYPE_MAP = {1: "photo", 2: "video"}

class InstagramAnalytics:
    def __init__(self, db_file: str = "instagram_analytics.db"):
        self.db_file = db_file
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Create profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                full_name TEXT,
                biography TEXT,
                follower_count INTEGER,
                following_count INTEGER,
                media_count INTEGER,
                is_verified BOOLEAN,
                is_private BOOLEAN,
                profile_pic_url TEXT,
                last_updated TIMESTAMP
            )
        ''')

        # Create media table (posts and reels)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media (
                id TEXT PRIMARY KEY,
                username TEXT,
                og_username TEXT,
                full_name TEXT,
                link TEXT,
                media_type TEXT,
                is_video BOOLEAN,
                carousel_media_count INTEGER,
                caption TEXT,
                post_datetime_ist TIMESTAMP,
                like_count INTEGER,
                comment_count INTEGER,
                reshare_count INTEGER,
                play_count INTEGER,
                is_collab BOOLEAN,
                collab_with TEXT,
                first_fetched TIMESTAMP,
                last_updated TIMESTAMP,
                raw_data TEXT
            )
        ''')

        # Create stories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stories (
                story_id TEXT PRIMARY KEY,
                username TEXT,
                og_username TEXT,
                full_name TEXT,
                media_type TEXT,
                post_datetime_ist TIMESTAMP,
                expire_datetime_ist TIMESTAMP,
                is_paid_partnership TEXT,
                is_reel_media BOOLEAN,
                first_fetched TIMESTAMP,
                raw_data TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def get_instagram_profile_data(self, username: str) -> Optional[Dict]:
        """Fetch Instagram profile data for a given username."""
        payload = {"username": username}
        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "starapi1.p.rapidapi.com",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.post(URL_PROFILE, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if (data and data["status"] == "done" and 
                data["response"]["body"]["data"]["user"]):
                user_data = data["response"]["body"]["data"]["user"]
                user_data["profile_id"] = user_data.get("id")
                user_data["username"] = username
                user_data["timestamp_ist"] = datetime.datetime.now(IST)
                return user_data
            else:
                print(f"Error fetching profile data for {username}: {data}")
                return None
        except Exception as e:
            print(f"Request error for profile {username}: {e}")
            return None

    def get_user_media(self, profile_id: str, count: int = 50) -> Optional[Dict]:
        """Fetch the last 'count' media items for a given profile ID."""
        payload = {"id": profile_id, "count": count}
        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "starapi1.p.rapidapi.com",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(URL_MEDIA, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching media for profile {profile_id}: {e}")
            return None

    def get_user_stories(self, profile_id: str) -> Optional[Dict]:
        """Fetch current stories for a given profile ID."""
        payload = {"ids": [profile_id]}
        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "starapi1.p.rapidapi.com",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(URL_STORIES, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching stories for profile {profile_id}: {e}")
            return None

    def process_media_item(self, item: Dict, og_username: str, profile_data: Dict) -> Dict:
        """Process a single media item and return structured data."""
        ts = item.get("taken_at", 0) or 0
        post_dt = datetime.datetime.fromtimestamp(ts, IST)
        
        code = item.get("code", "") or ""
        link = f"https://www.instagram.com/p/{code}/"
        
        coauthors = item.get("coauthor_producers") or []
        is_collab = bool(coauthors)
        collab_with = ", ".join(c.get("username", "") for c in coauthors)
        
        return {
            "id": str(item.get("id", "")),
            "username": item.get("user", {}).get("username", ""),
            "og_username": og_username,
            "full_name": item.get("user", {}).get("full_name", ""),
            "link": link,
            "media_type": MEDIA_TYPE_MAP.get(item.get("media_type", 0), ""),
            "is_video": item.get("is_video", False),
            "carousel_media_count": item.get("carousel_media_count", 0),
            "caption": item.get("caption", {}).get("text", "") if item.get("caption") else "",
            "post_datetime_ist": post_dt,
            "like_count": item.get("like_count", 0),
            "comment_count": item.get("comment_count", 0),
            "reshare_count": item.get("reshare_count", 0),
            "play_count": item.get("play_count", 0),
            "is_collab": is_collab,
            "collab_with": collab_with,
            "first_fetched": datetime.datetime.now(IST),
            "last_updated": datetime.datetime.now(IST),
            "raw_data": json.dumps(item)
        }

    def process_story_item(self, item: Dict, reel_meta: Dict, og_username: str) -> Dict:
        """Process a single story item and return structured data."""
        ts = item.get("taken_at", 0) or 0
        post_dt = datetime.datetime.fromtimestamp(ts, IST)
        
        exp_ts = reel_meta.get("expiring_at", 0) or 0
        exp_dt = datetime.datetime.fromtimestamp(exp_ts, IST)
        
        return {
            "story_id": str(item.get("id", "")),
            "username": reel_meta.get("user", {}).get("username", ""),
            "og_username": og_username,
            "full_name": reel_meta.get("user", {}).get("full_name", ""),
            "media_type": STORY_TYPE_MAP.get(item.get("media_type", 0), ""),
            "post_datetime_ist": post_dt,
            "expire_datetime_ist": exp_dt,
            "is_paid_partnership": "Yes" if reel_meta.get("is_paid_partnership") else "No",
            "is_reel_media": reel_meta.get("is_reel_media", False),
            "first_fetched": datetime.datetime.now(IST),
            "raw_data": json.dumps(item)
        }

    def save_profile_data(self, profile_data: Dict):
        """Save profile data to database."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO profiles
            (username, full_name, biography, follower_count, following_count,
             media_count, is_verified, is_private, profile_pic_url, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile_data.get('username'),
            profile_data.get('full_name', ''),
            profile_data.get('biography', ''),
            profile_data.get('edge_followed_by', {}).get('count', 0),
            profile_data.get('edge_follow', {}).get('count', 0),
            profile_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
            profile_data.get('is_verified', False),
            profile_data.get('is_private', False),
            profile_data.get('profile_pic_url', ''),
            datetime.datetime.now(IST)
        ))

        conn.commit()
        conn.close()

    def save_media_data(self, media_items: List[Dict]):
        """Save media data to database."""
        if not media_items:
            return

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        for item in media_items:
            cursor.execute('''
                INSERT OR REPLACE INTO media
                (id, username, og_username, full_name, link, media_type, is_video,
                 carousel_media_count, caption, post_datetime_ist, like_count,
                 comment_count, reshare_count, play_count, is_collab, collab_with,
                 first_fetched, last_updated, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['id'], item['username'], item['og_username'], item['full_name'],
                item['link'], item['media_type'], item['is_video'],
                item['carousel_media_count'], item['caption'], item['post_datetime_ist'],
                item['like_count'], item['comment_count'], item['reshare_count'],
                item['play_count'], item['is_collab'], item['collab_with'],
                item['first_fetched'], item['last_updated'], item['raw_data']
            ))

        conn.commit()
        conn.close()

    def save_stories_data(self, stories_items: List[Dict]):
        """Save stories data to database."""
        if not stories_items:
            return

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        for item in stories_items:
            cursor.execute('''
                INSERT OR REPLACE INTO stories
                (story_id, username, og_username, full_name, media_type,
                 post_datetime_ist, expire_datetime_ist, is_paid_partnership,
                 is_reel_media, first_fetched, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['story_id'], item['username'], item['og_username'],
                item['full_name'], item['media_type'], item['post_datetime_ist'],
                item['expire_datetime_ist'], item['is_paid_partnership'],
                item['is_reel_media'], item['first_fetched'], item['raw_data']
            ))

        conn.commit()
        conn.close()

    def fetch_data_for_username(self, username: str):
        """Fetch all data (profile, media, stories) for a single username."""
        print(f"Fetching data for {username}...")
        
        # Get profile data
        profile_data = self.get_instagram_profile_data(username)
        if not profile_data:
            print(f"Failed to fetch profile data for {username}")
            return
        
        self.save_profile_data(profile_data)
        profile_id = profile_data.get("profile_id")
        
        if not profile_id:
            print(f"No profile ID found for {username}")
            return
        
        # Get media data
        media_data = self.get_user_media(profile_id, count=50)
        media_items = []
        if media_data:
            items = media_data.get("response", {}).get("body", {}).get("items", [])
            for item in items:
                processed_item = self.process_media_item(item, username, profile_data)
                media_items.append(processed_item)
        
        self.save_media_data(media_items)
        print(f"Saved {len(media_items)} media items for {username}")
        
        # Get stories data
        stories_data = self.get_user_stories(profile_id)
        stories_items = []
        if stories_data:
            reel = stories_data.get("response", {}).get("body", {}).get("reels", {}).get(str(profile_id), {})
            if reel:
                for item in reel.get("items", []):
                    processed_story = self.process_story_item(item, reel, username)
                    stories_items.append(processed_story)
        
        self.save_stories_data(stories_items)
        print(f"Saved {len(stories_items)} stories for {username}")
        
        # Rate limiting
        time.sleep(2)

    def fetch_all_data(self):
        """Fetch data for all configured usernames."""
        print("Starting data fetch for all usernames...")
        for username in USERNAMES:
            self.fetch_data_for_username(username)
        print("Data fetch completed!")

    def get_media_dataframe(self) -> pd.DataFrame:
        """Get all media data as DataFrame."""
        conn = sqlite3.connect(self.db_file)
        query = '''
            SELECT * FROM media
            ORDER BY og_username ASC, post_datetime_ist DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            df['post_datetime_ist'] = pd.to_datetime(df['post_datetime_ist'])
            df['date'] = df['post_datetime_ist'].dt.date
        
        return df

    def get_profile_dataframe(self) -> pd.DataFrame:
        """Get all profile data as DataFrame."""
        conn = sqlite3.connect(self.db_file)
        df = pd.read_sql_query("SELECT * FROM profiles ORDER BY username", conn)
        conn.close()
        return df

    def get_stories_dataframe(self) -> pd.DataFrame:
        """Get all stories data as DataFrame."""
        conn = sqlite3.connect(self.db_file)
        query = '''
            SELECT * FROM stories
            WHERE expire_datetime_ist > datetime('now')
            ORDER BY og_username ASC, post_datetime_ist DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            df['post_datetime_ist'] = pd.to_datetime(df['post_datetime_ist'])
            df['expire_datetime_ist'] = pd.to_datetime(df['expire_datetime_ist'])
        
        return df

    def export_to_csv(self, output_dir: str = "exports"):
        """Export all data to CSV files."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Export profiles
        df_profiles = self.get_profile_dataframe()
        if not df_profiles.empty:
            df_profiles.to_csv(os.path.join(output_dir, "profiles.csv"), index=False)
            print(f"Exported {len(df_profiles)} profiles to profiles.csv")
        
        # Export media
        df_media = self.get_media_dataframe()
        if not df_media.empty:
            df_media.to_csv(os.path.join(output_dir, "media.csv"), index=False)
            print(f"Exported {len(df_media)} media items to media.csv")
        
        # Export stories
        df_stories = self.get_stories_dataframe()
        if not df_stories.empty:
            df_stories.to_csv(os.path.join(output_dir, "stories.csv"), index=False)
            print(f"Exported {len(df_stories)} stories to stories.csv")

    def get_performance_insights(self) -> Dict:
        """Generate basic performance insights."""
        df = self.get_media_dataframe()
        if df.empty:
            return {"error": "No data available"}
        
        insights = {}
        
        for username in df['og_username'].unique():
            user_df = df[df['og_username'] == username].copy()
            
            if len(user_df) == 0:
                continue
            
            # Calculate engagement rate (likes + comments per post)
            user_df['engagement'] = user_df['like_count'] + user_df['comment_count']
            
            # Top 5 performing posts
            top_5 = user_df.nlargest(5, 'engagement')[['link', 'media_type', 'engagement', 'post_datetime_ist']]
            
            # Bottom 5 performing posts
            bottom_5 = user_df.nsmallest(5, 'engagement')[['link', 'media_type', 'engagement', 'post_datetime_ist']]
            
            # Daily averages
            daily_stats = user_df.groupby('date').agg({
                'like_count': 'mean',
                'comment_count': 'mean',
                'engagement': 'mean'
            }).round(2)
            
            insights[username] = {
                'total_posts': len(user_df),
                'avg_likes': user_df['like_count'].mean(),
                'avg_comments': user_df['comment_count'].mean(),
                'avg_engagement': user_df['engagement'].mean(),
                'top_5_posts': top_5.to_dict('records'),
                'bottom_5_posts': bottom_5.to_dict('records'),
                'daily_averages': daily_stats.to_dict()
            }
        
        return insights

def main():
    """Main function to run the Instagram Analytics."""
    analytics = InstagramAnalytics()
    
    print("Instagram Social Media Analytics MVP")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Fetch fresh data from Instagram")
        print("2. View current data summary")
        print("3. Export data to CSV")
        print("4. Generate performance insights")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == "1":
            analytics.fetch_all_data()
        
        elif choice == "2":
            df_profiles = analytics.get_profile_dataframe()
            df_media = analytics.get_media_dataframe()
            df_stories = analytics.get_stories_dataframe()
            
            print(f"\nCurrent Data Summary:")
            print(f"Profiles: {len(df_profiles)}")
            print(f"Media items: {len(df_media)}")
            print(f"Active stories: {len(df_stories)}")
            
            if not df_media.empty:
                print(f"\nPosts by username:")
                for username in df_media['og_username'].unique():
                    count = len(df_media[df_media['og_username'] == username])
                    print(f"  {username}: {count} posts")
        
        elif choice == "3":
            analytics.export_to_csv()
        
        elif choice == "4":
            insights = analytics.get_performance_insights()
            if "error" in insights:
                print(insights["error"])
            else:
                for username, data in insights.items():
                    print(f"\n{username.upper()} Performance Insights:")
                    print(f"  Total posts: {data['total_posts']}")
                    print(f"  Avg likes: {data['avg_likes']:.1f}")
                    print(f"  Avg comments: {data['avg_comments']:.1f}")
                    print(f"  Avg engagement: {data['avg_engagement']:.1f}")
                    
                    print(f"\n  Top 5 performing posts:")
                    for i, post in enumerate(data['top_5_posts'][:5], 1):
                        print(f"    {i}. {post['engagement']} engagement - {post['link']}")
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main()
