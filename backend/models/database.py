from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    instagram_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), nullable=False, index=True)
    full_name = db.Column(db.String(200))
    biography = db.Column(db.Text)
    profile_pic_url = db.Column(db.String(500))
    profile_pic_url_hd = db.Column(db.String(500))
    external_url = db.Column(db.String(500))
    
    # Follower counts
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    media_count = db.Column(db.Integer, default=0)
    
    # Account status
    is_private = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_business_account = db.Column(db.Boolean, default=False)
    business_category_name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    
    # Additional data
    highlight_reel_count = db.Column(db.Integer, default=0)
    has_ar_effects = db.Column(db.Boolean, default=False)
    has_clips = db.Column(db.Boolean, default=False)
    has_guides = db.Column(db.Boolean, default=False)
    has_channel = db.Column(db.Boolean, default=False)
    has_blocked_viewer = db.Column(db.Boolean, default=False)
    blocked_by_viewer = db.Column(db.Boolean, default=False)
    country_block = db.Column(db.Boolean, default=False)
    followed_by_viewer = db.Column(db.Boolean, default=False)
    follows_viewer = db.Column(db.Boolean, default=False)
    has_requested_viewer = db.Column(db.Boolean, default=False)
    requested_by_viewer = db.Column(db.Boolean, default=False)
    
    # Contact info
    business_email = db.Column(db.String(200))
    business_phone_number = db.Column(db.String(50))
    business_address_json = db.Column(db.Text)  # JSON string
    
    # Platform data
    pronouns = db.Column(db.Text)  # JSON array
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped_at = db.Column(db.DateTime)
    
    # Relationships
    media_posts = db.relationship('MediaPost', backref='profile', lazy='dynamic', cascade='all, delete-orphan')
    stories = db.relationship('Story', backref='profile', lazy='dynamic', cascade='all, delete-orphan')
    follower_data = db.relationship('FollowerData', backref='profile', lazy='dynamic', cascade='all, delete-orphan')
    api_requests = db.relationship('ApiRequestLog', backref='profile', lazy='dynamic', cascade='all, delete-orphan')

    @classmethod
    def upsert(cls, instagram_id, **kwargs):
        """Upsert profile data - create or update existing profile"""
        profile = cls.query.filter_by(instagram_id=instagram_id).first()
        
        if profile:
            # Update existing profile
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.updated_at = datetime.utcnow()
        else:
            # Create new profile
            kwargs['instagram_id'] = instagram_id
            kwargs['created_at'] = datetime.utcnow()
            kwargs['updated_at'] = datetime.utcnow()
            profile = cls(**kwargs)
            db.session.add(profile)
        
        try:
            db.session.commit()
            return profile, True
        except Exception as e:
            db.session.rollback()
            raise e

    def to_dict(self):
        return {
            'id': self.id,
            'instagram_id': self.instagram_id,
            'username': self.username,
            'full_name': self.full_name,
            'biography': self.biography,
            'profile_pic_url': self.profile_pic_url,
            'profile_pic_url_hd': self.profile_pic_url_hd,
            'external_url': self.external_url,
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'media_count': self.media_count,
            'is_private': self.is_private,
            'is_verified': self.is_verified,
            'is_business_account': self.is_business_account,
            'business_category_name': self.business_category_name,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_scraped_at': self.last_scraped_at.isoformat() if self.last_scraped_at else None
        }

class MediaPost(db.Model):
    __tablename__ = 'media_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    instagram_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False, index=True)
    shortcode = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Media info
    media_type = db.Column(db.String(20), nullable=False)  # 'photo', 'video', 'carousel'
    caption = db.Column(db.Text)
    display_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    video_view_count = db.Column(db.Integer, default=0)
    is_video = db.Column(db.Boolean, default=False)
    
    # Dimensions
    dimensions_height = db.Column(db.Integer)
    dimensions_width = db.Column(db.Integer)
    
    # Engagement
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    comments_disabled = db.Column(db.Boolean, default=False)
    
    # Timestamps
    taken_at_timestamp = db.Column(db.DateTime)
    
    # Additional fields
    accessibility_caption = db.Column(db.Text)
    is_ad = db.Column(db.Boolean, default=False)
    is_paid_partnership = db.Column(db.Boolean, default=False)
    product_type = db.Column(db.String(50))
    
    # Location
    location_id = db.Column(db.String(50))
    location_name = db.Column(db.String(200))
    location_slug = db.Column(db.String(200))
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped_at = db.Column(db.DateTime)
    
    # Relationships
    comments = db.relationship('MediaComment', backref='media_post', lazy='dynamic', cascade='all, delete-orphan')
    hashtag_data = db.relationship('HashtagData', backref='media_post', lazy='dynamic', cascade='all, delete-orphan')

    @classmethod
    def upsert(cls, instagram_id, profile_id, **kwargs):
        """Upsert media post data"""
        media = cls.query.filter_by(instagram_id=instagram_id).first()
        
        if media:
            # Update existing media
            for key, value in kwargs.items():
                if hasattr(media, key):
                    setattr(media, key, value)
            media.updated_at = datetime.utcnow()
        else:
            # Create new media
            kwargs['instagram_id'] = instagram_id
            kwargs['profile_id'] = profile_id
            kwargs['created_at'] = datetime.utcnow()
            kwargs['updated_at'] = datetime.utcnow()
            media = cls(**kwargs)
            db.session.add(media)
        
        try:
            db.session.commit()
            return media, True
        except Exception as e:
            db.session.rollback()
            raise e

    def to_dict(self):
        return {
            'id': self.id,
            'instagram_id': self.instagram_id,
            'shortcode': self.shortcode,
            'media_type': self.media_type,
            'caption': self.caption,
            'display_url': self.display_url,
            'video_url': self.video_url,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'video_view_count': self.video_view_count,
            'taken_at_timestamp': self.taken_at_timestamp.isoformat() if self.taken_at_timestamp else None,
            'is_video': self.is_video,
            'location_name': self.location_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Story(db.Model):
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    instagram_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False, index=True)
    
    # Story info
    media_type = db.Column(db.String(20))  # 'photo', 'video'
    display_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    
    # Dimensions
    dimensions_height = db.Column(db.Integer)
    dimensions_width = db.Column(db.Integer)
    
    # Timestamps
    taken_at_timestamp = db.Column(db.DateTime)
    expiring_at_timestamp = db.Column(db.DateTime)
    
    # Story features
    has_audio = db.Column(db.Boolean, default=False)
    is_video = db.Column(db.Boolean, default=False)
    video_duration = db.Column(db.Float)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def upsert(cls, instagram_id, profile_id, **kwargs):
        """Upsert story data"""
        story = cls.query.filter_by(instagram_id=instagram_id).first()
        
        if story:
            # Update existing story
            for key, value in kwargs.items():
                if hasattr(story, key):
                    setattr(story, key, value)
            story.updated_at = datetime.utcnow()
        else:
            # Create new story
            kwargs['instagram_id'] = instagram_id
            kwargs['profile_id'] = profile_id
            kwargs['created_at'] = datetime.utcnow()
            kwargs['updated_at'] = datetime.utcnow()
            story = cls(**kwargs)
            db.session.add(story)
        
        try:
            db.session.commit()
            return story, True
        except Exception as e:
            db.session.rollback()
            raise e

class MediaComment(db.Model):
    __tablename__ = 'media_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    instagram_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    media_post_id = db.Column(db.Integer, db.ForeignKey('media_posts.id'), nullable=False, index=True)
    
    # Comment info
    text = db.Column(db.Text)
    created_at_utc = db.Column(db.DateTime)
    like_count = db.Column(db.Integer, default=0)
    
    # Author info
    owner_username = db.Column(db.String(100))
    owner_id = db.Column(db.String(50))
    owner_profile_pic_url = db.Column(db.String(500))
    owner_is_verified = db.Column(db.Boolean, default=False)
    
    # Reply info
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('media_comments.id'), nullable=True)
    reply_count = db.Column(db.Integer, default=0)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for replies
    replies = db.relationship('MediaComment', backref=db.backref('parent_comment', remote_side=[id]), lazy='dynamic')

    @classmethod
    def upsert(cls, instagram_id, media_post_id, **kwargs):
        """Upsert comment data"""
        comment = cls.query.filter_by(instagram_id=instagram_id).first()
        
        if comment:
            # Update existing comment
            for key, value in kwargs.items():
                if hasattr(comment, key):
                    setattr(comment, key, value)
            comment.updated_at = datetime.utcnow()
        else:
            # Create new comment
            kwargs['instagram_id'] = instagram_id
            kwargs['media_post_id'] = media_post_id
            kwargs['created_at'] = datetime.utcnow()
            kwargs['updated_at'] = datetime.utcnow()
            comment = cls(**kwargs)
            db.session.add(comment)
        
        try:
            db.session.commit()
            return comment, True
        except Exception as e:
            db.session.rollback()
            raise e

class FollowerData(db.Model):
    __tablename__ = 'follower_data'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False, index=True)
    
    # Follower counts tracking over time
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    media_count = db.Column(db.Integer, default=0)
    
    # Daily tracking
    date_recorded = db.Column(db.Date, nullable=False, index=True)
    
    # Growth metrics
    followers_gained = db.Column(db.Integer, default=0)
    followers_lost = db.Column(db.Integer, default=0)
    net_follower_change = db.Column(db.Integer, default=0)
    
    # Engagement metrics
    avg_likes_per_post = db.Column(db.Float, default=0.0)
    avg_comments_per_post = db.Column(db.Float, default=0.0)
    engagement_rate = db.Column(db.Float, default=0.0)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate daily records
    __table_args__ = (db.UniqueConstraint('profile_id', 'date_recorded', name='unique_daily_follower_data'),)

    @classmethod
    def upsert(cls, profile_id, date_recorded, **kwargs):
        """Upsert follower data for a specific date"""
        follower_data = cls.query.filter_by(profile_id=profile_id, date_recorded=date_recorded).first()
        
        if follower_data:
            # Update existing record
            for key, value in kwargs.items():
                if hasattr(follower_data, key):
                    setattr(follower_data, key, value)
        else:
            # Create new record
            kwargs['profile_id'] = profile_id
            kwargs['date_recorded'] = date_recorded
            kwargs['created_at'] = datetime.utcnow()
            follower_data = cls(**kwargs)
            db.session.add(follower_data)
        
        try:
            db.session.commit()
            return follower_data, True
        except Exception as e:
            db.session.rollback()
            raise e

class HashtagData(db.Model):
    __tablename__ = 'hashtag_data'
    
    id = db.Column(db.Integer, primary_key=True)
    media_post_id = db.Column(db.Integer, db.ForeignKey('media_posts.id'), nullable=False, index=True)
    
    # Hashtag info
    hashtag = db.Column(db.String(200), nullable=False, index=True)
    hashtag_count = db.Column(db.Integer, default=0)  # Number of posts with this hashtag
    
    # Position in caption
    position_in_caption = db.Column(db.Integer)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def upsert_hashtags(cls, media_post_id, hashtags_list):
        """Upsert multiple hashtags for a media post"""
        # First, delete existing hashtags for this post
        cls.query.filter_by(media_post_id=media_post_id).delete()
        
        # Add new hashtags
        for idx, hashtag in enumerate(hashtags_list):
            hashtag_data = cls(
                media_post_id=media_post_id,
                hashtag=hashtag.strip('#').lower(),
                position_in_caption=idx,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(hashtag_data)
        
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

class ApiRequestLog(db.Model):
    __tablename__ = 'api_request_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=True, index=True)  # Nullable for general API calls
    
    # Request info
    endpoint = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), default='GET')
    request_url = db.Column(db.Text)
    
    # Response info
    status_code = db.Column(db.Integer)
    response_time_ms = db.Column(db.Integer)
    success = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text)
    
    # Data tracking
    data_type = db.Column(db.String(50))  # 'profile', 'media', 'stories', 'comments', 'followers'
    records_processed = db.Column(db.Integer, default=0)
    records_created = db.Column(db.Integer, default=0)
    records_updated = db.Column(db.Integer, default=0)
    
    # Rate limiting
    rate_limit_remaining = db.Column(db.Integer)
    rate_limit_reset_at = db.Column(db.DateTime)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    @classmethod
    def log_request(cls, endpoint, method='GET', profile_id=None, **kwargs):
        """Log an API request with detailed information"""
        log_entry = cls(
            profile_id=profile_id,
            endpoint=endpoint,
            method=method,
            created_at=datetime.utcnow(),
            **kwargs
        )
        
        db.session.add(log_entry)
        
        try:
            db.session.commit()
            return log_entry
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_recent_requests(cls, profile_id=None, limit=50):
        """Get recent API requests, optionally filtered by profile"""
        query = cls.query.order_by(cls.created_at.desc())
        
        if profile_id:
            query = query.filter_by(profile_id=profile_id)
        
        return query.limit(limit).all()

    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'success': self.success,
            'error_message': self.error_message,
            'data_type': self.data_type,
            'records_processed': self.records_processed,
            'records_created': self.records_created,
            'records_updated': self.records_updated,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Utility functions for bulk operations
def bulk_upsert_profiles(profiles_data):
    """Bulk upsert multiple profiles"""
    results = []
    for profile_data in profiles_data:
        instagram_id = profile_data.pop('instagram_id')
        profile, created = Profile.upsert(instagram_id, **profile_data)
        results.append({'profile': profile, 'created': created})
    return results

def bulk_upsert_media_posts(media_data_list):
    """Bulk upsert multiple media posts"""
    results = []
    for media_data in media_data_list:
        instagram_id = media_data.pop('instagram_id')
        profile_id = media_data.pop('profile_id')
        media, created = MediaPost.upsert(instagram_id, profile_id, **media_data)
        results.append({'media': media, 'created': created})
    return results

def bulk_upsert_comments(comments_data_list):
    """Bulk upsert multiple comments"""
    results = []
    for comment_data in comments_data_list:
        instagram_id = comment_data.pop('instagram_id')
        media_post_id = comment_data.pop('media_post_id')
        comment, created = MediaComment.upsert(instagram_id, media_post_id, **comment_data)
        results.append({'comment': comment, 'created': created})
    return results

def extract_hashtags_from_caption(caption):
    """Extract hashtags from Instagram caption"""
    if not caption:
        return []
    
    import re
    hashtag_pattern = r'#[a-zA-Z0-9_]+'
    hashtags = re.findall(hashtag_pattern, caption)
    return [tag.lower() for tag in hashtags]

def calculate_engagement_rate(likes, comments, followers):
    """Calculate engagement rate percentage"""
    if followers == 0:
        return 0.0
    return ((likes + comments) / followers) * 100
