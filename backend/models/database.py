"""
Database models for Instagram Analytics
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()
IST = pytz.timezone("Asia/Kolkata")

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    username = db.Column(db.String(100), primary_key=True)
    full_name = db.Column(db.String(200))
    biography = db.Column(db.Text)
    follower_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    media_count = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    is_private = db.Column(db.Boolean, default=False)
    profile_pic_url = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    
    # Relationships
    media_posts = db.relationship('MediaPost', backref='profile_owner', lazy='dynamic')
    stories = db.relationship('Story', backref='profile_owner', lazy='dynamic')
    
    def to_dict(self):
        return {
            'username': self.username,
            'full_name': self.full_name,
            'biography': self.biography,
            'follower_count': self.follower_count,
            'following_count': self.following_count,
            'media_count': self.media_count,
            'is_verified': self.is_verified,
            'is_private': self.is_private,
            'profile_pic_url': self.profile_pic_url,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class MediaPost(db.Model):
    __tablename__ = 'media_posts'
    
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(100), db.ForeignKey('profiles.username'))
    og_username = db.Column(db.String(100))  # Original username we're tracking
    full_name = db.Column(db.String(200))
    link = db.Column(db.Text)
    media_type = db.Column(db.String(20))  # post, reel, carousel
    is_video = db.Column(db.Boolean, default=False)
    carousel_media_count = db.Column(db.Integer, default=0)
    caption = db.Column(db.Text)
    post_datetime_ist = db.Column(db.DateTime)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    reshare_count = db.Column(db.Integer, default=0)
    play_count = db.Column(db.Integer, default=0)
    is_collab = db.Column(db.Boolean, default=False)
    collab_with = db.Column(db.Text)
    first_fetched = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)  # Store raw API response
    
    # Computed properties
    @property
    def engagement_count(self):
        return (self.like_count or 0) + (self.comment_count or 0)
    
    @property
    def post_date(self):
        return self.post_datetime_ist.date() if self.post_datetime_ist else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'og_username': self.og_username,
            'full_name': self.full_name,
            'link': self.link,
            'media_type': self.media_type,
            'is_video': self.is_video,
            'carousel_media_count': self.carousel_media_count,
            'caption': self.caption,
            'post_datetime_ist': self.post_datetime_ist.isoformat() if self.post_datetime_ist else None,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'reshare_count': self.reshare_count,
            'play_count': self.play_count,
            'is_collab': self.is_collab,
            'collab_with': self.collab_with,
            'engagement_count': self.engagement_count,
            'first_fetched': self.first_fetched.isoformat() if self.first_fetched else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class Story(db.Model):
    __tablename__ = 'stories'
    
    story_id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(100), db.ForeignKey('profiles.username'))
    og_username = db.Column(db.String(100))
    full_name = db.Column(db.String(200))
    media_type = db.Column(db.String(20))  # photo, video
    post_datetime_ist = db.Column(db.DateTime)
    expire_datetime_ist = db.Column(db.DateTime)
    is_paid_partnership = db.Column(db.String(10), default='No')
    is_reel_media = db.Column(db.Boolean, default=False)
    first_fetched = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'story_id': self.story_id,
            'username': self.username,
            'og_username': self.og_username,
            'full_name': self.full_name,
            'media_type': self.media_type,
            'post_datetime_ist': self.post_datetime_ist.isoformat() if self.post_datetime_ist else None,
            'expire_datetime_ist': self.expire_datetime_ist.isoformat() if self.expire_datetime_ist else None,
            'is_paid_partnership': self.is_paid_partnership,
            'is_reel_media': self.is_reel_media,
            'first_fetched': self.first_fetched.isoformat() if self.first_fetched else None
        }

# Analytics tracking table for historical data
class DailyMetrics(db.Model):
    __tablename__ = 'daily_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), db.ForeignKey('profiles.username'))
    date = db.Column(db.Date)
    follower_count = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)
    total_likes = db.Column(db.Integer, default=0)
    total_comments = db.Column(db.Integer, default=0)
    total_engagement = db.Column(db.Integer, default=0)
    avg_engagement_per_post = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'date': self.date.isoformat() if self.date else None,
            'follower_count': self.follower_count,
            'posts_count': self.posts_count,
            'total_likes': self.total_likes,
            'total_comments': self.total_comments,
            'total_engagement': self.total_engagement,
            'avg_engagement_per_post': self.avg_engagement_per_post,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
