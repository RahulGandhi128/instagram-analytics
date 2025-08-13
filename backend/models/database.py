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
    user_id = db.Column(db.String(50))  # Instagram user ID
    full_name = db.Column(db.String(200))
    biography = db.Column(db.Text)
    follower_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    media_count = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    is_private = db.Column(db.Boolean, default=False)
    is_business_account = db.Column(db.Boolean, default=False)
    profile_pic_url = db.Column(db.Text)
    external_url = db.Column(db.Text)
    category = db.Column(db.String(100))
    business_category = db.Column(db.String(100))
    country_block = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    
    # Enhanced analytics fields
    avg_engagement_rate = db.Column(db.Float, default=0.0)
    total_posts_tracked = db.Column(db.Integer, default=0)
    total_stories_tracked = db.Column(db.Integer, default=0)
    total_highlights = db.Column(db.Integer, default=0)
    
    # Raw data storage
    raw_profile_data = db.Column(db.JSON)
    
    # Relationships
    media_posts = db.relationship('MediaPost', backref='profile_owner', lazy='dynamic')
    stories = db.relationship('Story', backref='profile_owner', lazy='dynamic')
    highlights = db.relationship('Highlight', backref='profile_owner', lazy='dynamic')
    followers_data = db.relationship('FollowerData', backref='profile_owner', lazy='dynamic')
    
    def to_dict(self):
        return {
            'username': self.username,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'biography': self.biography,
            'follower_count': self.follower_count,
            'following_count': self.following_count,
            'media_count': self.media_count,
            'is_verified': self.is_verified,
            'is_private': self.is_private,
            'is_business_account': self.is_business_account,
            'profile_pic_url': self.profile_pic_url,
            'external_url': self.external_url,
            'category': self.category,
            'business_category': self.business_category,
            'avg_engagement_rate': self.avg_engagement_rate,
            'total_posts_tracked': self.total_posts_tracked,
            'total_stories_tracked': self.total_stories_tracked,
            'total_highlights': self.total_highlights,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class MediaPost(db.Model):
    __tablename__ = 'media_posts'
    
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(100), db.ForeignKey('profiles.username'))
    og_username = db.Column(db.String(100))  # Original username we're tracking
    full_name = db.Column(db.String(200))
    shortcode = db.Column(db.String(50))  # Instagram shortcode
    link = db.Column(db.Text)
    media_type = db.Column(db.String(20))  # post, reel, carousel, video
    is_video = db.Column(db.Boolean, default=False)
    carousel_media_count = db.Column(db.Integer, default=0)
    caption = db.Column(db.Text)
    hashtags = db.Column(db.JSON)  # Extracted hashtags
    mentions = db.Column(db.JSON)  # Extracted mentions
    post_datetime_ist = db.Column(db.DateTime)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    reshare_count = db.Column(db.Integer, default=0)
    play_count = db.Column(db.Integer, default=0)
    video_view_count = db.Column(db.Integer, default=0)
    is_collab = db.Column(db.Boolean, default=False)
    collab_with = db.Column(db.Text)
    is_ad = db.Column(db.Boolean, default=False)
    is_sponsored = db.Column(db.Boolean, default=False)
    location_name = db.Column(db.String(200))
    location_id = db.Column(db.String(50))
    
    # Enhanced engagement metrics
    engagement_rate = db.Column(db.Float, default=0.0)
    save_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    
    # Tracking fields
    first_fetched = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    data_quality_score = db.Column(db.Float, default=1.0)  # 0-1 score for data completeness
    
    # Raw data storage
    raw_data = db.Column(db.JSON)  # Store raw API response
    
    # Computed properties
    @property
    def engagement_count(self):
        return (self.like_count or 0) + (self.comment_count or 0) + (self.save_count or 0)
    
    @property
    def post_date(self):
        return self.post_datetime_ist.date() if self.post_datetime_ist else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'og_username': self.og_username,
            'full_name': self.full_name,
            'shortcode': self.shortcode,
            'link': self.link,
            'media_type': self.media_type,
            'is_video': self.is_video,
            'carousel_media_count': self.carousel_media_count,
            'caption': self.caption,
            'hashtags': self.hashtags,
            'mentions': self.mentions,
            'post_datetime_ist': self.post_datetime_ist.isoformat() if self.post_datetime_ist else None,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'reshare_count': self.reshare_count,
            'play_count': self.play_count,
            'video_view_count': self.video_view_count,
            'is_collab': self.is_collab,
            'collab_with': self.collab_with,
            'is_ad': self.is_ad,
            'is_sponsored': self.is_sponsored,
            'location_name': self.location_name,
            'engagement_rate': self.engagement_rate,
            'save_count': self.save_count,
            'share_count': self.share_count,
            'engagement_count': self.engagement_count,
            'first_fetched': self.first_fetched.isoformat() if self.first_fetched else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'data_quality_score': self.data_quality_score
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

# New enhanced models for comprehensive data
class Highlight(db.Model):
    __tablename__ = 'highlights'
    
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(100), db.ForeignKey('profiles.username'))
    title = db.Column(db.String(200))
    cover_url = db.Column(db.Text)
    stories_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'title': self.title,
            'cover_url': self.cover_url,
            'stories_count': self.stories_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class FollowerData(db.Model):
    __tablename__ = 'follower_data'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), db.ForeignKey('profiles.username'))
    follower_username = db.Column(db.String(100))
    follower_full_name = db.Column(db.String(200))
    follower_pic_url = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    is_private = db.Column(db.Boolean, default=False)
    follower_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    collected_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'follower_username': self.follower_username,
            'follower_full_name': self.follower_full_name,
            'follower_pic_url': self.follower_pic_url,
            'is_verified': self.is_verified,
            'is_private': self.is_private,
            'follower_count': self.follower_count,
            'following_count': self.following_count,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None
        }

class MediaComment(db.Model):
    __tablename__ = 'media_comments'
    
    id = db.Column(db.String(50), primary_key=True)
    media_id = db.Column(db.String(50), db.ForeignKey('media_posts.id'))
    comment_text = db.Column(db.Text)
    commenter_username = db.Column(db.String(100))
    commenter_full_name = db.Column(db.String(200))
    commenter_pic_url = db.Column(db.Text)
    like_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime)
    collected_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'media_id': self.media_id,
            'comment_text': self.comment_text,
            'commenter_username': self.commenter_username,
            'commenter_full_name': self.commenter_full_name,
            'like_count': self.like_count,
            'reply_count': self.reply_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None
        }

class HashtagData(db.Model):
    __tablename__ = 'hashtag_data'
    
    id = db.Column(db.Integer, primary_key=True)
    hashtag = db.Column(db.String(100))
    post_count = db.Column(db.Integer, default=0)
    engagement_count = db.Column(db.Integer, default=0)
    trending_score = db.Column(db.Float, default=0.0)
    collected_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hashtag': self.hashtag,
            'post_count': self.post_count,
            'engagement_count': self.engagement_count,
            'trending_score': self.trending_score,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None
        }

# Enhanced models for Star API comprehensive data collection

class LocationData(db.Model):
    __tablename__ = 'location_data'
    
    id = db.Column(db.String(50), primary_key=True)  # Instagram location ID
    name = db.Column(db.String(200))
    slug = db.Column(db.String(200))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    website = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    post_count = db.Column(db.Integer, default=0)
    profile_pic_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'phone': self.phone,
            'website': self.website,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'post_count': self.post_count,
            'profile_pic_url': self.profile_pic_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SimilarAccount(db.Model):
    __tablename__ = 'similar_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    base_username = db.Column(db.String(100), db.ForeignKey('profiles.username'))
    similar_username = db.Column(db.String(100))
    similar_user_id = db.Column(db.String(50))
    similar_full_name = db.Column(db.String(200))
    similar_profile_pic_url = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    is_private = db.Column(db.Boolean, default=False)
    follower_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    media_count = db.Column(db.Integer, default=0)
    similarity_score = db.Column(db.Float, default=0.0)
    collected_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'base_username': self.base_username,
            'similar_username': self.similar_username,
            'similar_user_id': self.similar_user_id,
            'similar_full_name': self.similar_full_name,
            'similar_profile_pic_url': self.similar_profile_pic_url,
            'is_verified': self.is_verified,
            'is_private': self.is_private,
            'follower_count': self.follower_count,
            'following_count': self.following_count,
            'media_count': self.media_count,
            'similarity_score': self.similarity_score,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None
        }

class UserSearchResult(db.Model):
    __tablename__ = 'user_search_results'
    
    id = db.Column(db.Integer, primary_key=True)
    search_query = db.Column(db.String(200))
    user_id = db.Column(db.String(50))
    username = db.Column(db.String(100))
    full_name = db.Column(db.String(200))
    profile_pic_url = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    is_private = db.Column(db.Boolean, default=False)
    follower_count = db.Column(db.Integer, default=0)
    search_rank = db.Column(db.Integer, default=0)
    searched_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'search_query': self.search_query,
            'user_id': self.user_id,
            'username': self.username,
            'full_name': self.full_name,
            'profile_pic_url': self.profile_pic_url,
            'is_verified': self.is_verified,
            'is_private': self.is_private,
            'follower_count': self.follower_count,
            'search_rank': self.search_rank,
            'searched_at': self.searched_at.isoformat() if self.searched_at else None
        }

class LocationSearchResult(db.Model):
    __tablename__ = 'location_search_results'
    
    id = db.Column(db.Integer, primary_key=True)
    search_query = db.Column(db.String(200))
    location_id = db.Column(db.String(50))
    name = db.Column(db.String(200))
    slug = db.Column(db.String(200))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    search_rank = db.Column(db.Integer, default=0)
    searched_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'search_query': self.search_query,
            'location_id': self.location_id,
            'name': self.name,
            'slug': self.slug,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'search_rank': self.search_rank,
            'searched_at': self.searched_at.isoformat() if self.searched_at else None
        }

class AudioData(db.Model):
    __tablename__ = 'audio_data'
    
    id = db.Column(db.String(50), primary_key=True)  # Audio asset ID
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(200))
    artist_name = db.Column(db.String(200))
    artist_username = db.Column(db.String(100))
    artist_id = db.Column(db.String(50))
    duration_ms = db.Column(db.Integer, default=0)
    is_explicit = db.Column(db.Boolean, default=False)
    is_eligible_for_vinyl_sticker = db.Column(db.Boolean, default=False)
    music_canonical_id = db.Column(db.String(50))
    cover_artwork_url = db.Column(db.Text)
    progressive_download_url = db.Column(db.Text)
    fast_start_progressive_download_url = db.Column(db.Text)
    dash_manifest = db.Column(db.Text)
    audio_cluster_id = db.Column(db.String(50))
    highlight_start_times_ms = db.Column(db.JSON)  # Array of start times
    collected_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'artist_name': self.artist_name,
            'artist_username': self.artist_username,
            'artist_id': self.artist_id,
            'duration_ms': self.duration_ms,
            'is_explicit': self.is_explicit,
            'is_eligible_for_vinyl_sticker': self.is_eligible_for_vinyl_sticker,
            'music_canonical_id': self.music_canonical_id,
            'cover_artwork_url': self.cover_artwork_url,
            'highlight_start_times_ms': self.highlight_start_times_ms,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AudioSearchResult(db.Model):
    __tablename__ = 'audio_search_results'
    
    id = db.Column(db.Integer, primary_key=True)
    search_query = db.Column(db.String(200))
    audio_id = db.Column(db.String(50))
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(200))
    artist_name = db.Column(db.String(200))
    artist_username = db.Column(db.String(100))
    duration_ms = db.Column(db.Integer, default=0)
    search_rank = db.Column(db.Integer, default=0)
    searched_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'search_query': self.search_query,
            'audio_id': self.audio_id,
            'title': self.title,
            'subtitle': self.subtitle,
            'artist_name': self.artist_name,
            'artist_username': self.artist_username,
            'duration_ms': self.duration_ms,
            'search_rank': self.search_rank,
            'searched_at': self.searched_at.isoformat() if self.searched_at else None
        }

class CommentReply(db.Model):
    __tablename__ = 'comment_replies'
    
    id = db.Column(db.String(50), primary_key=True)
    parent_comment_id = db.Column(db.String(50), db.ForeignKey('media_comments.id'))
    media_id = db.Column(db.String(50), db.ForeignKey('media_posts.id'))
    reply_text = db.Column(db.Text)
    replier_username = db.Column(db.String(100))
    replier_full_name = db.Column(db.String(200))
    replier_pic_url = db.Column(db.Text)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime)
    collected_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'parent_comment_id': self.parent_comment_id,
            'media_id': self.media_id,
            'reply_text': self.reply_text,
            'replier_username': self.replier_username,
            'replier_full_name': self.replier_full_name,
            'like_count': self.like_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None
        }

class CommentLike(db.Model):
    __tablename__ = 'comment_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.String(50), db.ForeignKey('media_comments.id'))
    liker_username = db.Column(db.String(100))
    liker_full_name = db.Column(db.String(200))
    liker_pic_url = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    liked_at = db.Column(db.DateTime)
    collected_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'comment_id': self.comment_id,
            'liker_username': self.liker_username,
            'liker_full_name': self.liker_full_name,
            'is_verified': self.is_verified,
            'liked_at': self.liked_at.isoformat() if self.liked_at else None,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None
        }

class HighlightStory(db.Model):
    __tablename__ = 'highlight_stories'
    
    id = db.Column(db.String(50), primary_key=True)
    highlight_id = db.Column(db.String(50), db.ForeignKey('highlights.id'))
    username = db.Column(db.String(100), db.ForeignKey('profiles.username'))
    story_type = db.Column(db.String(20))  # photo, video
    taken_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    media_url = db.Column(db.Text)
    thumbnail_url = db.Column(db.Text)
    has_audio = db.Column(db.Boolean, default=False)
    video_duration = db.Column(db.Float, default=0.0)
    collected_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    raw_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'highlight_id': self.highlight_id,
            'username': self.username,
            'story_type': self.story_type,
            'taken_at': self.taken_at.isoformat() if self.taken_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'has_audio': self.has_audio,
            'video_duration': self.video_duration,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None
        }

# Enhanced table for comprehensive data tracking
class DataCollectionLog(db.Model):
    __tablename__ = 'data_collection_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), db.ForeignKey('profiles.username'))
    data_type = db.Column(db.String(50))  # user_info, media, stories, highlights, etc.
    endpoint_used = db.Column(db.String(100))  # Which Star API endpoint was used
    status = db.Column(db.String(20))  # success, error, partial
    records_collected = db.Column(db.Integer, default=0)
    api_response_time_ms = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    collected_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'data_type': self.data_type,
            'endpoint_used': self.endpoint_used,
            'status': self.status,
            'records_collected': self.records_collected,
            'api_response_time_ms': self.api_response_time_ms,
            'error_message': self.error_message,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None
        }
