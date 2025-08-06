"""
Instagram Analytics Service - Enhanced version with PostgreSQL support
"""
import requests
import pandas as pd
import datetime
import pytz
from typing import Dict, List, Optional
import json
import time
from models.database import db, Profile, MediaPost, Story, DailyMetrics
from sqlalchemy import func, desc, and_
import numpy as np
from collections import defaultdict

# Configuration
USERNAMES = ["naukridotcom", "swiggyindia", "zomato", "instagram"]

# API Endpoints
URL_PROFILE = "https://starapi1.p.rapidapi.com/instagram/user/get_web_profile_info"
URL_MEDIA = "https://starapi1.p.rapidapi.com/instagram/user/get_media"
URL_STORIES = "https://starapi1.p.rapidapi.com/instagram/user/get_stories"

# Timezone setup
IST = pytz.timezone("Asia/Kolkata")

# Media type mappings
MEDIA_TYPE_MAP = {1: "post", 2: "reel", 8: "carousel"}
STORY_TYPE_MAP = {1: "photo", 2: "video"}

class InstagramAnalyticsService:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_instagram_profile_data(self, username: str) -> Optional[Dict]:
        """Fetch Instagram profile data for a given username."""
        payload = {"username": username}
        headers = {
            "x-rapidapi-key": self.api_key,
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
            "x-rapidapi-key": self.api_key,
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
            "x-rapidapi-key": self.api_key,
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

    def save_profile_data(self, profile_data: Dict):
        """Save or update profile data in database."""
        try:
            profile = Profile.query.get(profile_data.get('username'))
            
            if profile:
                # Update existing profile
                profile.full_name = profile_data.get('full_name', '')
                profile.biography = profile_data.get('biography', '')
                profile.follower_count = profile_data.get('edge_followed_by', {}).get('count', 0)
                profile.following_count = profile_data.get('edge_follow', {}).get('count', 0)
                profile.media_count = profile_data.get('edge_owner_to_timeline_media', {}).get('count', 0)
                profile.is_verified = profile_data.get('is_verified', False)
                profile.is_private = profile_data.get('is_private', False)
                profile.profile_pic_url = profile_data.get('profile_pic_url', '')
                profile.last_updated = datetime.datetime.now(IST)
            else:
                # Create new profile
                profile = Profile(
                    username=profile_data.get('username'),
                    full_name=profile_data.get('full_name', ''),
                    biography=profile_data.get('biography', ''),
                    follower_count=profile_data.get('edge_followed_by', {}).get('count', 0),
                    following_count=profile_data.get('edge_follow', {}).get('count', 0),
                    media_count=profile_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                    is_verified=profile_data.get('is_verified', False),
                    is_private=profile_data.get('is_private', False),
                    profile_pic_url=profile_data.get('profile_pic_url', ''),
                    last_updated=datetime.datetime.now(IST)
                )
                db.session.add(profile)
            
            db.session.commit()
            return profile
        except Exception as e:
            db.session.rollback()
            print(f"Error saving profile data: {e}")
            return None

    def save_media_post(self, item: Dict, og_username: str, profile_data: Dict):
        """Save or update a media post."""
        try:
            ts = item.get("taken_at", 0) or 0
            post_dt = datetime.datetime.fromtimestamp(ts, IST)
            
            code = item.get("code", "") or ""
            link = f"https://www.instagram.com/p/{code}/"
            
            coauthors = item.get("coauthor_producers") or []
            is_collab = bool(coauthors)
            collab_with = ", ".join(c.get("username", "") for c in coauthors)
            
            post_id = str(item.get("id", ""))
            
            # Check if post already exists
            existing_post = MediaPost.query.get(post_id)
            
            if existing_post:
                # Update engagement metrics
                existing_post.like_count = item.get("like_count", 0)
                existing_post.comment_count = item.get("comment_count", 0)
                existing_post.reshare_count = item.get("reshare_count", 0)
                existing_post.play_count = item.get("play_count", 0)
                existing_post.last_updated = datetime.datetime.now(IST)
            else:
                # Create new post
                media_post = MediaPost(
                    id=post_id,
                    username=item.get("user", {}).get("username", ""),
                    og_username=og_username,
                    full_name=item.get("user", {}).get("full_name", ""),
                    link=link,
                    media_type=MEDIA_TYPE_MAP.get(item.get("media_type", 0), ""),
                    is_video=item.get("is_video", False),
                    carousel_media_count=item.get("carousel_media_count", 0),
                    caption=item.get("caption", {}).get("text", "") if item.get("caption") else "",
                    post_datetime_ist=post_dt,
                    like_count=item.get("like_count", 0),
                    comment_count=item.get("comment_count", 0),
                    reshare_count=item.get("reshare_count", 0),
                    play_count=item.get("play_count", 0),
                    is_collab=is_collab,
                    collab_with=collab_with,
                    first_fetched=datetime.datetime.now(IST),
                    last_updated=datetime.datetime.now(IST),
                    raw_data=item
                )
                db.session.add(media_post)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error saving media post: {e}")
            return False

    def save_story(self, item: Dict, reel_meta: Dict, og_username: str):
        """Save a story."""
        try:
            ts = item.get("taken_at", 0) or 0
            post_dt = datetime.datetime.fromtimestamp(ts, IST)
            
            exp_ts = reel_meta.get("expiring_at", 0) or 0
            exp_dt = datetime.datetime.fromtimestamp(exp_ts, IST)
            
            story_id = str(item.get("id", ""))
            
            # Check if story already exists
            existing_story = Story.query.get(story_id)
            
            if not existing_story:
                story = Story(
                    story_id=story_id,
                    username=reel_meta.get("user", {}).get("username", ""),
                    og_username=og_username,
                    full_name=reel_meta.get("user", {}).get("full_name", ""),
                    media_type=STORY_TYPE_MAP.get(item.get("media_type", 0), ""),
                    post_datetime_ist=post_dt,
                    expire_datetime_ist=exp_dt,
                    is_paid_partnership="Yes" if reel_meta.get("is_paid_partnership") else "No",
                    is_reel_media=reel_meta.get("is_reel_media", False),
                    first_fetched=datetime.datetime.now(IST),
                    raw_data=item
                )
                db.session.add(story)
                db.session.commit()
            
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error saving story: {e}")
            return False

    def fetch_data_for_username(self, username: str):
        """Fetch all data for a username and save to database."""
        print(f"Fetching data for {username}...")
        
        # Get profile data
        profile_data = self.get_instagram_profile_data(username)
        if not profile_data:
            print(f"Failed to fetch profile data for {username}")
            return False
        
        # Save profile
        profile = self.save_profile_data(profile_data)
        if not profile:
            return False
        
        profile_id = profile_data.get("profile_id")
        if not profile_id:
            print(f"No profile ID found for {username}")
            return False
        
        # Get and save media data
        media_data = self.get_user_media(profile_id, count=50)
        media_count = 0
        if media_data:
            items = media_data.get("response", {}).get("body", {}).get("items", [])
            for item in items:
                if self.save_media_post(item, username, profile_data):
                    media_count += 1
        
        print(f"Saved {media_count} media items for {username}")
        
        # Get and save stories
        stories_data = self.get_user_stories(profile_id)
        stories_count = 0
        if stories_data:
            reel = stories_data.get("response", {}).get("body", {}).get("reels", {}).get(str(profile_id), {})
            if reel:
                for item in reel.get("items", []):
                    if self.save_story(item, reel, username):
                        stories_count += 1
        
        print(f"Saved {stories_count} stories for {username}")
        
        # Calculate and save daily metrics
        self.calculate_daily_metrics(username)
        
        # Rate limiting
        time.sleep(2)
        return True

    def calculate_daily_metrics(self, username: str):
        """Calculate and save daily metrics for a username."""
        try:
            today = datetime.datetime.now().date()
            
            # Check if metrics already exist for today
            existing_metric = DailyMetrics.query.filter_by(
                username=username, 
                date=today
            ).first()
            
            # Get profile data
            profile = Profile.query.get(username)
            if not profile:
                return
            
            # Calculate today's metrics
            posts_today = MediaPost.query.filter(
                MediaPost.og_username == username,
                func.date(MediaPost.post_datetime_ist) == today
            ).all()
            
            total_likes = sum(post.like_count or 0 for post in posts_today)
            total_comments = sum(post.comment_count or 0 for post in posts_today)
            total_engagement = total_likes + total_comments
            avg_engagement = total_engagement / len(posts_today) if posts_today else 0
            
            if existing_metric:
                # Update existing metric
                existing_metric.follower_count = profile.follower_count
                existing_metric.posts_count = len(posts_today)
                existing_metric.total_likes = total_likes
                existing_metric.total_comments = total_comments
                existing_metric.total_engagement = total_engagement
                existing_metric.avg_engagement_per_post = avg_engagement
            else:
                # Create new metric
                daily_metric = DailyMetrics(
                    username=username,
                    date=today,
                    follower_count=profile.follower_count,
                    posts_count=len(posts_today),
                    total_likes=total_likes,
                    total_comments=total_comments,
                    total_engagement=total_engagement,
                    avg_engagement_per_post=avg_engagement
                )
                db.session.add(daily_metric)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error calculating daily metrics for {username}: {e}")

    def fetch_all_data(self):
        """Fetch data for all configured usernames."""
        print("Starting data fetch for all usernames...")
        for username in USERNAMES:
            self.fetch_data_for_username(username)
        print("Data fetch completed!")

    def get_performance_insights(self, username: str = None, days: int = 30) -> Dict:
        """Get comprehensive performance insights."""
        try:
            # Date range
            end_date = datetime.datetime.now().date()
            start_date = end_date - datetime.timedelta(days=days)
            
            query = MediaPost.query.filter(
                func.date(MediaPost.post_datetime_ist).between(start_date, end_date)
            )
            
            if username:
                query = query.filter(MediaPost.og_username == username)
            
            posts = query.all()
            
            if not posts:
                return {"error": "No data available for the specified period"}
            
            insights = {}
            
            # Group by username if no specific username provided
            usernames = [username] if username else list(set(post.og_username for post in posts))
            
            for uname in usernames:
                user_posts = [post for post in posts if post.og_username == uname]
                
                if not user_posts:
                    continue
                
                # Basic stats
                total_posts = len(user_posts)
                total_likes = sum(post.like_count or 0 for post in user_posts)
                total_comments = sum(post.comment_count or 0 for post in user_posts)
                total_engagement = total_likes + total_comments
                
                avg_likes = total_likes / total_posts if total_posts > 0 else 0
                avg_comments = total_comments / total_posts if total_posts > 0 else 0
                avg_engagement = total_engagement / total_posts if total_posts > 0 else 0
                
                # Top and bottom performing posts
                user_posts_sorted = sorted(user_posts, key=lambda x: x.engagement_count, reverse=True)
                top_posts = user_posts_sorted[:5]
                bottom_posts = user_posts_sorted[-5:] if len(user_posts_sorted) >= 5 else user_posts_sorted
                
                # Media type analysis
                media_type_stats = defaultdict(lambda: {'count': 0, 'total_engagement': 0})
                for post in user_posts:
                    media_type_stats[post.media_type]['count'] += 1
                    media_type_stats[post.media_type]['total_engagement'] += post.engagement_count
                
                # Calculate average engagement by media type
                for media_type in media_type_stats:
                    stats = media_type_stats[media_type]
                    stats['avg_engagement'] = stats['total_engagement'] / stats['count'] if stats['count'] > 0 else 0
                
                # Day-wise analysis
                daily_stats = defaultdict(lambda: {'posts': 0, 'engagement': 0})
                for post in user_posts:
                    if post.post_datetime_ist:
                        day = post.post_datetime_ist.strftime('%A')
                        daily_stats[day]['posts'] += 1
                        daily_stats[day]['engagement'] += post.engagement_count
                
                # Hour-wise analysis for optimal posting times
                hourly_stats = defaultdict(lambda: {'posts': 0, 'engagement': 0})
                for post in user_posts:
                    if post.post_datetime_ist:
                        hour = post.post_datetime_ist.hour
                        hourly_stats[hour]['posts'] += 1
                        hourly_stats[hour]['engagement'] += post.engagement_count
                
                # Calculate average engagement per hour
                for hour in hourly_stats:
                    stats = hourly_stats[hour]
                    stats['avg_engagement'] = stats['engagement'] / stats['posts'] if stats['posts'] > 0 else 0
                
                # Find optimal posting times (top 3 hours by average engagement)
                optimal_hours = sorted(
                    [(hour, stats) for hour, stats in hourly_stats.items()], 
                    key=lambda x: x[1]['avg_engagement'], 
                    reverse=True
                )[:3]
                
                insights[uname] = {
                    'basic_stats': {
                        'total_posts': total_posts,
                        'total_likes': total_likes,
                        'total_comments': total_comments,
                        'total_engagement': total_engagement,
                        'avg_likes': round(avg_likes, 2),
                        'avg_comments': round(avg_comments, 2),
                        'avg_engagement': round(avg_engagement, 2)
                    },
                    'top_posts': [
                        {
                            'link': post.link,
                            'media_type': post.media_type,
                            'engagement': post.engagement_count,
                            'likes': post.like_count,
                            'comments': post.comment_count,
                            'post_date': post.post_datetime_ist.isoformat() if post.post_datetime_ist else None
                        } for post in top_posts
                    ],
                    'bottom_posts': [
                        {
                            'link': post.link,
                            'media_type': post.media_type,
                            'engagement': post.engagement_count,
                            'likes': post.like_count,
                            'comments': post.comment_count,
                            'post_date': post.post_datetime_ist.isoformat() if post.post_datetime_ist else None
                        } for post in bottom_posts
                    ],
                    'media_type_analysis': dict(media_type_stats),
                    'daily_analysis': dict(daily_stats),
                    'optimal_posting_times': [
                        {
                            'hour': f"{hour:02d}:00",
                            'avg_engagement': round(stats['avg_engagement'], 2),
                            'posts_count': stats['posts']
                        } for hour, stats in optimal_hours if stats['posts'] > 0
                    ]
                }
            
            return insights
            
        except Exception as e:
            print(f"Error generating performance insights: {e}")
            return {"error": str(e)}

    def get_weekly_comparison(self, username: str = None, period: str = 'week') -> Dict:
        """Get period-over-period comparison data based on most recent data."""
        try:
            # Get all posts for the username, ordered by date
            base_query = MediaPost.query
            if username:
                base_query = base_query.filter(MediaPost.og_username == username)
            
            all_posts = base_query.filter(MediaPost.post_datetime_ist.isnot(None)).order_by(MediaPost.post_datetime_ist.desc()).limit(200).all()
            
            if not all_posts:
                return {}
            
            # Get the most recent post date and calculate periods based on type
            most_recent_date = all_posts[0].post_datetime_ist.date()
            
            if period == 'week':
                current_period_start = most_recent_date - datetime.timedelta(days=7)
                previous_period_start = current_period_start - datetime.timedelta(days=7)
                period_label = 'Week'
            elif period == 'month':
                current_period_start = most_recent_date - datetime.timedelta(days=30)
                previous_period_start = current_period_start - datetime.timedelta(days=30)
                period_label = 'Month'
            else:  # custom - 14 days each
                current_period_start = most_recent_date - datetime.timedelta(days=14)
                previous_period_start = current_period_start - datetime.timedelta(days=14)
                period_label = 'Custom (14 days)'
            
            comparison = {}
            
            # Group by username
            if username:
                usernames = [username]
            else:
                usernames = list(set([p.og_username for p in all_posts]))
            
            for uname in usernames:
                user_posts = [p for p in all_posts if p.og_username == uname]
                
                # Split posts into two periods relative to most recent data
                current_period_posts = [p for p in user_posts if p.post_datetime_ist.date() > current_period_start]
                previous_period_posts = [p for p in user_posts if previous_period_start < p.post_datetime_ist.date() <= current_period_start]
                
                # Calculate totals for current period
                current_total_engagement = sum(p.engagement_count for p in current_period_posts)
                current_total_posts = len(current_period_posts)
                current_avg_engagement = current_total_engagement / current_total_posts if current_total_posts > 0 else 0
                
                # Calculate totals for previous period
                previous_total_engagement = sum(p.engagement_count for p in previous_period_posts)
                previous_total_posts = len(previous_period_posts)
                previous_avg_engagement = previous_total_engagement / previous_total_posts if previous_total_posts > 0 else 0
                
                # Calculate percentage changes
                engagement_change = ((current_total_engagement - previous_total_engagement) / previous_total_engagement * 100) if previous_total_engagement > 0 else (100 if current_total_engagement > 0 else 0)
                posts_change = ((current_total_posts - previous_total_posts) / previous_total_posts * 100) if previous_total_posts > 0 else (100 if current_total_posts > 0 else 0)
                
                comparison[uname] = {
                    'current_week': {
                        'total_engagement': current_total_engagement,
                        'total_posts': current_total_posts,
                        'avg_engagement_per_post': round(current_avg_engagement, 2)
                    },
                    'previous_week': {
                        'total_engagement': previous_total_engagement,
                        'total_posts': previous_total_posts,
                        'avg_engagement_per_post': round(previous_avg_engagement, 2)
                    },
                    'changes': {
                        'engagement_change_percent': round(engagement_change, 2),
                        'posts_change_percent': round(posts_change, 2)
                    },
                    'date_range': {
                        'current_period_start': current_period_start.isoformat(),
                        'previous_period_start': previous_period_start.isoformat(),
                        'most_recent_post': most_recent_date.isoformat(),
                        'period_type': period_label
                    }
                }
            
            return comparison
            
        except Exception as e:
            print(f"Error generating period comparison: {e}")
            return {"error": str(e)}
