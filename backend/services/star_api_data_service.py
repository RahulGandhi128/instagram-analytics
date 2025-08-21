"""
Star API Data Service - Comprehensive data collection and storage
Handles all Star API data types with UPSERT strategy and relationship management
"""
from models.database import (
    db, Profile, MediaPost, Story, FollowerData, MediaComment, 
    HashtagData, ApiRequestLog
)
from services.star_api_service import create_star_api_service
from datetime import datetime, timezone
import logging
import json
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StarApiDataService:
    """
    Comprehensive data service for Star API integration with intelligent UPSERT strategy
    Follows the same pattern as DATABASE_SERVICE_DOCUMENTATION.md
    """
    
    def __init__(self, api_key: str):
        self.star_service = create_star_api_service(api_key)
        self.logger = logging.getLogger(__name__)
    
    def collect_comprehensive_data(self, username: str) -> dict:
        """
        Comprehensive data collection following the documented UPSERT strategy
        Collects all available data types for a user
        """
        # Default configuration - collect everything
        default_config = {
            'profile': True,
            'media_posts': True,
            'comments': True,
            'stories': False,
            'highlights': False,
            'followers': False,
            'following': False,
            'similar_accounts': False
        }
        default_limits = {
            'media_posts': 50,
            'comments_per_post': 20,
            'stories': 20,
            'highlights': 10,
            'followers': 100,
            'following': 100
        }
        
        return self.collect_comprehensive_data_with_config(username, default_config, default_limits)
    
    def collect_comprehensive_data_with_config(self, username: str, dataTypes: dict, limits: dict) -> dict:
        """
        Comprehensive data collection with user-defined configuration
        """
        results = {
            'username': username,
            'status': 'success',
            'data_collected': {},
            'errors': [],
            'config_used': {
                'dataTypes': dataTypes,
                'limits': limits
            }
        }
        
        try:
            # 1. Get user info first to establish profile
            if dataTypes.get('profile', True):
                user_info = self._collect_user_profile(username)
                if user_info:
                    results['data_collected']['profile'] = user_info
                    
                    # Get user_id for subsequent calls
                    user_id = user_info.get('user_id')
                    if user_id:
                        # 2. Collect media posts
                        if dataTypes.get('media_posts', True):
                            media_result = self._collect_user_media(username, user_id, limits.get('media_posts', 50))
                            results['data_collected']['media'] = media_result
                        
                        # 3. Collect stories
                        if dataTypes.get('stories', False):
                            stories_result = self._collect_user_stories(username, user_id, limits.get('stories', 20))
                            results['data_collected']['stories'] = stories_result
                        
                        # 4. Collect highlights
                        if dataTypes.get('highlights', False):
                            highlights_result = self._collect_user_highlights(username, user_id, limits.get('highlights', 10))
                            results['data_collected']['highlights'] = highlights_result
                        
                        # 5. Collect followers sample
                        if dataTypes.get('followers', False):
                            followers_result = self._collect_user_followers(username, user_id, limits.get('followers', 100))
                            results['data_collected']['followers'] = followers_result
                        
                        # 6. Collect following sample
                        if dataTypes.get('following', False):
                            following_result = self._collect_user_following(username, user_id, limits.get('following', 100))
                            results['data_collected']['following'] = following_result
                        
                        # 7. Collect similar accounts
                        if dataTypes.get('similar_accounts', False):
                            similar_result = self._collect_similar_accounts(username, user_id)
                            results['data_collected']['similar_accounts'] = similar_result
                        
                        # 8. Collect comments for media posts (with rate limiting)
                        if dataTypes.get('comments', False) and dataTypes.get('media_posts', True):
                            comments_result = self._collect_media_comments(username, user_id, limits.get('comments_per_post', 20))
                            results['data_collected']['comments'] = comments_result
                        
                        # 9. Update profile analytics
                        self._update_profile_analytics(username)
                else:
                    results['status'] = 'error'
                    results['errors'].append('Failed to collect profile information')
            else:
                results['status'] = 'error'
                results['errors'].append('Profile collection is required but was disabled')
                    
        except Exception as e:
            self.logger.error(f"Error in comprehensive data collection for {username}: {e}")
            results['status'] = 'error'
            results['errors'].append(str(e))
        
        return results
    
    def _collect_user_profile(self, username: str) -> dict:
        """Collect and store user profile data with UPSERT strategy"""
        start_time = datetime.now()
        
        try:
            # Get profile data from Star API
            api_response = self.star_service.get_user_info_by_username(username)
            
            if not api_response or api_response.get('status') != 'done':
                self._log_collection('user_info', username, 'error', 0, 
                                   error_message="Failed to fetch user info")
                return {'status': 'error', 'message': 'Failed to fetch user info'}
            
            # Extract user data from API response
            user_data = self._extract_user_data(api_response)
            
            if not user_data:
                return {'status': 'error', 'message': 'No user data found'}
            
            # UPSERT Profile using documented strategy
            existing_profile = db.session.query(Profile).filter_by(username=username).first()
            
            if existing_profile:
                # UPDATE: Preserve historical data, update current metrics
                existing_profile.full_name = user_data.get('full_name')
                existing_profile.biography = user_data.get('biography')
                existing_profile.followers_count = user_data.get('follower_count', 0)
                existing_profile.following_count = user_data.get('following_count', 0)
                existing_profile.media_count = user_data.get('media_count', 0)
                existing_profile.is_verified = user_data.get('is_verified', False)
                existing_profile.is_private = user_data.get('is_private', False)
                existing_profile.is_business_account = user_data.get('is_business_account', False)
                existing_profile.profile_pic_url = user_data.get('profile_pic_url')
                existing_profile.external_url = user_data.get('external_url')
                existing_profile.category = user_data.get('category')
                existing_profile.business_category = user_data.get('business_category')
                existing_profile.last_updated = datetime.now()
                existing_profile.raw_profile_data = api_response
                
                profile = existing_profile
            else:
                # INSERT: New profile with complete data
                profile = Profile(
                    username=username,
                    user_id=user_data.get('user_id'),
                    full_name=user_data.get('full_name'),
                    biography=user_data.get('biography'),
                    followers_count=user_data.get('follower_count', 0),
                    following_count=user_data.get('following_count', 0),
                    media_count=user_data.get('media_count', 0),
                    is_verified=user_data.get('is_verified', False),
                    is_private=user_data.get('is_private', False),
                    is_business_account=user_data.get('is_business_account', False),
                    profile_pic_url=user_data.get('profile_pic_url'),
                    external_url=user_data.get('external_url'),
                    category=user_data.get('category'),
                    business_category=user_data.get('business_category'),
                    raw_profile_data=api_response
                )
                db.session.add(profile)
            
            db.session.commit()
            
            # Log successful collection
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._log_collection('user_info', username, 'success', 1, response_time)
            
            profile_dict = profile.to_dict()
            profile_dict['user_id'] = user_data.get('user_id')
            return profile_dict
            
        except Exception as e:
            self.logger.error(f"Error collecting user profile for {username}: {e}")
            self._log_collection('user_info', username, 'error', 0, 
                               error_message=str(e))
            return {'status': 'error', 'message': str(e)}
    
    def _collect_user_media(self, username: str, user_id: str, limit: int = 50) -> dict:
        """Collect and store user media with UPSERT strategy"""
        start_time = datetime.now()
        
        try:
            api_response = self.star_service.get_user_media(user_id, count=limit)
            
            if not api_response or api_response.get('status') != 'done':
                self._log_collection('user_media', username, 'error', 0)
                return {'status': 'error', 'count': 0}
            
            media_items = self._extract_media_data(api_response)
            collected_count = 0
            
            for media_item in media_items:
                # UPSERT MediaPost using documented strategy
                existing_post = db.session.query(MediaPost).filter_by(instagram_id=media_item['id']).first()
                
                if existing_post:
                    # UPDATE: Preserve history, update engagement
                    existing_post.like_count = media_item.get('like_count', 0)
                    existing_post.comment_count = media_item.get('comment_count', 0)
                    existing_post.video_view_count = media_item.get('video_view_count', 0)
                    existing_post.updated_at = datetime.now()
                else:
                    # Get profile for foreign key
                    profile = db.session.query(Profile).filter_by(username=username).first()
                    
                    # INSERT: New post with complete data
                    new_post = MediaPost(
                        instagram_id=media_item['id'],  # Use instagram_id instead of id
                        profile_id=profile.id if profile else None,
                        shortcode=media_item.get('shortcode'),
                        media_type=media_item.get('media_type'),
                        caption=media_item.get('caption'),
                        display_url=media_item.get('display_url'),
                        is_video=media_item.get('is_video', False),
                        taken_at_timestamp=media_item.get('post_datetime_ist'),
                        like_count=media_item.get('like_count', 0),
                        comment_count=media_item.get('comment_count', 0),
                        video_view_count=media_item.get('video_view_count', 0),
                        location_name=media_item.get('location_name'),
                        location_id=media_item.get('location_id')
                    )
                    db.session.add(new_post)
                
                collected_count += 1
            
            db.session.commit()
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._log_collection('user_media', username, 'success', collected_count, response_time)
            
            return {'status': 'success', 'count': collected_count}
            
        except Exception as e:
            self.logger.error(f"Error collecting user media for {username}: {e}")
            self._log_collection('user_media', username, 'error', 0, error_message=str(e))
            return {'status': 'error', 'count': 0}
    
    def _collect_user_stories(self, username: str, user_id: str) -> dict:
        """Collect and store user stories"""
        start_time = datetime.now()
        
        try:
            api_response = self.star_service.get_user_stories(user_id)
            
            if not api_response or not api_response.get('success'):
                self._log_collection('user_stories', username, 'error', 0)
                return {'status': 'error', 'count': 0}
            
            story_items = self._extract_story_data(api_response)
            collected_count = 0
            
            for story_item in story_items:
                # UPSERT Story
                existing_story = db.session.query(Story).filter_by(story_id=story_item['story_id']).first()
                
                if not existing_story:
                    new_story = Story(
                        story_id=story_item['story_id'],
                        username=username,
                        og_username=username,
                        full_name=story_item.get('full_name'),
                        media_type=story_item.get('media_type'),
                        post_datetime_ist=story_item.get('post_datetime_ist'),
                        expire_datetime_ist=story_item.get('expire_datetime_ist'),
                        is_paid_partnership=story_item.get('is_paid_partnership', 'No'),
                        is_reel_media=story_item.get('is_reel_media', False),
                        raw_data=story_item.get('raw_data', {})
                    )
                    db.session.add(new_story)
                    collected_count += 1
            
            db.session.commit()
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._log_collection('user_stories', username, 'success', collected_count, response_time)
            
            return {'status': 'success', 'count': collected_count}
            
        except Exception as e:
            self.logger.error(f"Error collecting user stories for {username}: {e}")
            self._log_collection('user_stories', username, 'error', 0, error_message=str(e))
            return {'status': 'error', 'count': 0}
    
    def _collect_user_highlights(self, username: str, user_id: str) -> dict:
        """Collect and store user highlights"""
        start_time = datetime.now()
        
        try:
            api_response = self.star_service.get_user_highlights(user_id)
            
            if not api_response or not api_response.get('success'):
                self._log_collection('user_highlights', username, 'error', 0)
                return {'status': 'error', 'count': 0}
            
            highlight_items = self._extract_highlight_data(api_response)
            collected_count = 0
            
            for highlight_item in highlight_items:
                # UPSERT Highlight
                existing_highlight = db.session.query(Highlight).filter_by(id=highlight_item['id']).first()
                
                if existing_highlight:
                    existing_highlight.title = highlight_item.get('title')
                    existing_highlight.cover_url = highlight_item.get('cover_url')
                    existing_highlight.stories_count = highlight_item.get('stories_count', 0)
                    existing_highlight.updated_at = datetime.now()
                    existing_highlight.raw_data = highlight_item.get('raw_data', {})
                else:
                    new_highlight = Highlight(
                        id=highlight_item['id'],
                        username=username,
                        title=highlight_item.get('title'),
                        cover_url=highlight_item.get('cover_url'),
                        stories_count=highlight_item.get('stories_count', 0),
                        created_at=highlight_item.get('created_at'),
                        raw_data=highlight_item.get('raw_data', {})
                    )
                    db.session.add(new_highlight)
                
                collected_count += 1
            
            db.session.commit()
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._log_collection('user_highlights', username, 'success', collected_count, response_time)
            
            return {'status': 'success', 'count': collected_count}
            
        except Exception as e:
            self.logger.error(f"Error collecting user highlights for {username}: {e}")
            self._log_collection('user_highlights', username, 'error', 0, error_message=str(e))
            return {'status': 'error', 'count': 0}
    
    def _collect_user_followers(self, username: str, user_id: str, count: int = 50) -> dict:
        """Collect and store user followers sample"""
        start_time = datetime.now()
        
        try:
            api_response = self.star_service.get_user_followers(user_id, count)
            
            if not api_response or not api_response.get('success'):
                self._log_collection('user_followers', username, 'error', 0)
                return {'status': 'error', 'count': 0}
            
            follower_items = self._extract_follower_data(api_response)
            collected_count = 0
            
            for follower_item in follower_items:
                # Check if already exists
                existing_follower = db.session.query(FollowerData).filter_by(
                    username=username,
                    follower_username=follower_item['follower_username']
                ).first()
                
                if not existing_follower:
                    new_follower = FollowerData(
                        username=username,
                        follower_username=follower_item['follower_username'],
                        follower_full_name=follower_item.get('follower_full_name'),
                        follower_pic_url=follower_item.get('follower_pic_url'),
                        is_verified=follower_item.get('is_verified', False),
                        is_private=follower_item.get('is_private', False),
                        follower_count=follower_item.get('follower_count', 0),
                        following_count=follower_item.get('following_count', 0),
                        raw_data=follower_item.get('raw_data', {})
                    )
                    db.session.add(new_follower)
                    collected_count += 1
            
            db.session.commit()
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._log_collection('user_followers', username, 'success', collected_count, response_time)
            
            return {'status': 'success', 'count': collected_count}
            
        except Exception as e:
            self.logger.error(f"Error collecting user followers for {username}: {e}")
            self._log_collection('user_followers', username, 'error', 0, error_message=str(e))
            return {'status': 'error', 'count': 0}
    
    def _collect_user_following(self, username: str, user_id: str, count: int = 50) -> dict:
        """Collect and store user following sample"""
        # Similar implementation to followers
        return {'status': 'success', 'count': 0}  # Placeholder
    
    def _collect_similar_accounts(self, username: str, user_id: str) -> dict:
        """Collect and store similar accounts"""
        start_time = datetime.now()
        
        try:
            api_response = self.star_service.get_similar_accounts(user_id)
            
            if not api_response or not api_response.get('success'):
                self._log_collection('similar_accounts', username, 'error', 0)
                return {'status': 'error', 'count': 0}
            
            similar_items = self._extract_similar_accounts_data(api_response)
            collected_count = 0
            
            for similar_item in similar_items:
                # Check if already exists
                existing_similar = db.session.query(SimilarAccount).filter_by(
                    base_username=username,
                    similar_username=similar_item['similar_username']
                ).first()
                
                if not existing_similar:
                    new_similar = SimilarAccount(
                        base_username=username,
                        similar_username=similar_item['similar_username'],
                        similar_user_id=similar_item.get('similar_user_id'),
                        similar_full_name=similar_item.get('similar_full_name'),
                        similar_profile_pic_url=similar_item.get('similar_profile_pic_url'),
                        is_verified=similar_item.get('is_verified', False),
                        is_private=similar_item.get('is_private', False),
                        follower_count=similar_item.get('follower_count', 0),
                        following_count=similar_item.get('following_count', 0),
                        media_count=similar_item.get('media_count', 0),
                        similarity_score=similar_item.get('similarity_score', 0.0),
                        raw_data=similar_item.get('raw_data', {})
                    )
                    db.session.add(new_similar)
                    collected_count += 1
            
            db.session.commit()
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._log_collection('similar_accounts', username, 'success', collected_count, response_time)
            
            return {'status': 'success', 'count': collected_count}
            
        except Exception as e:
            self.logger.error(f"Error collecting similar accounts for {username}: {e}")
            self._log_collection('similar_accounts', username, 'error', 0, error_message=str(e))
            return {'status': 'error', 'count': 0}
    
    def _collect_media_comments(self, username: str, user_id: str, comments_per_post: int = 20) -> dict:
        """Collect comments for all media posts with rate limiting"""
        start_time = datetime.now()
        
        try:
            # Get all media posts for this user
            media_posts = db.session.query(MediaPost).filter_by(profile_id=user_id).all()
            
            if not media_posts:
                return {'status': 'success', 'count': 0, 'message': 'No media posts found'}
            
            total_comments = 0
            successful_posts = 0
            
            self.logger.info(f"Collecting comments for {len(media_posts)} media posts")
            
            for i, post in enumerate(media_posts):
                try:
                    # Rate limiting: wait between requests
                    if i > 0:
                        import time
                        time.sleep(2)  # 2 second delay between requests
                    
                    # Collect comments for this post
                    comments_result = self._collect_post_comments(post.shortcode, post.id)
                    
                    if comments_result['status'] == 'success':
                        total_comments += comments_result['count']
                        successful_posts += 1
                        self.logger.info(f"Collected {comments_result['count']} comments for post {post.shortcode}")
                    else:
                        self.logger.warning(f"Failed to collect comments for post {post.shortcode}: {comments_result.get('message', 'Unknown error')}")
                
                except Exception as e:
                    self.logger.error(f"Error collecting comments for post {post.shortcode}: {e}")
                    continue
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._log_collection('media_comments', username, 'success', total_comments, response_time)
            
            return {
                'status': 'success', 
                'count': total_comments, 
                'posts_processed': successful_posts,
                'total_posts': len(media_posts)
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting media comments for {username}: {e}")
            self._log_collection('media_comments', username, 'error', 0, error_message=str(e))
            return {'status': 'error', 'count': 0}
    
    def _collect_post_comments(self, shortcode: str, media_post_id: int) -> dict:
        """Collect comments for a specific media post"""
        try:
            # Get comments from Star API
            api_response = self.star_service.get_media_comments(shortcode)
            
            if not api_response or api_response.get('status') != 'done':
                return {'status': 'error', 'count': 0, 'message': 'Failed to fetch comments'}
            
            # Extract comments from API response
            comments_data = self._extract_comments_data(api_response)
            
            if not comments_data:
                return {'status': 'success', 'count': 0, 'message': 'No comments found'}
            
            # Store comments in database
            collected_count = 0
            for comment_data in comments_data:
                try:
                    MediaComment.upsert(
                        instagram_id=comment_data['instagram_id'],
                        media_post_id=media_post_id,
                        text=comment_data['text'],
                        created_at_utc=comment_data['created_at_utc'],
                        like_count=comment_data['like_count'],
                        owner_username=comment_data['owner_username'],
                        owner_id=comment_data['owner_id'],
                        owner_profile_pic_url=comment_data['owner_profile_pic_url'],
                        owner_is_verified=comment_data['owner_is_verified'],
                        parent_comment_id=comment_data.get('parent_comment_id'),
                        reply_count=comment_data.get('reply_count', 0)
                    )
                    collected_count += 1
                except Exception as e:
                    self.logger.error(f"Error storing comment {comment_data.get('instagram_id')}: {e}")
                    continue
            
            return {'status': 'success', 'count': collected_count}
            
        except Exception as e:
            self.logger.error(f"Error collecting comments for post {shortcode}: {e}")
            return {'status': 'error', 'count': 0, 'message': str(e)}
    
    def _extract_comments_data(self, api_response: dict) -> list:
        """Extract comments data from Star API response"""
        comments = []
        try:
            if 'response' in api_response and 'body' in api_response['response']:
                body = api_response['response']['body']
                
                # Handle different response formats
                if 'data' in body and 'shortcode_media' in body['data']:
                    media_data = body['data']['shortcode_media']
                    comments_data = media_data.get('edge_media_to_parent_comment', {}).get('edges', [])
                    
                    for comment_edge in comments_data:
                        comment_node = comment_edge.get('node', {})
                        owner = comment_node.get('owner', {})
                        
                        comment = {
                            'instagram_id': str(comment_node.get('id', '')),
                            'text': comment_node.get('text', ''),
                            'created_at_utc': datetime.fromtimestamp(comment_node.get('created_at', 0)),
                            'like_count': comment_node.get('edge_liked_by', {}).get('count', 0),
                            'owner_username': owner.get('username', ''),
                            'owner_id': str(owner.get('id', '')),
                            'owner_profile_pic_url': owner.get('profile_pic_url', ''),
                            'owner_is_verified': owner.get('is_verified', False),
                            'parent_comment_id': None,  # Top-level comments
                            'reply_count': comment_node.get('edge_threaded_comments', {}).get('count', 0)
                        }
                        comments.append(comment)
                        
                        # Also collect replies if available
                        replies_data = comment_node.get('edge_threaded_comments', {}).get('edges', [])
                        for reply_edge in replies_data:
                            reply_node = reply_edge.get('node', {})
                            reply_owner = reply_node.get('owner', {})
                            
                            reply = {
                                'instagram_id': str(reply_node.get('id', '')),
                                'text': reply_node.get('text', ''),
                                'created_at_utc': datetime.fromtimestamp(reply_node.get('created_at', 0)),
                                'like_count': reply_node.get('edge_liked_by', {}).get('count', 0),
                                'owner_username': reply_owner.get('username', ''),
                                'owner_id': str(reply_owner.get('id', '')),
                                'owner_profile_pic_url': reply_owner.get('profile_pic_url', ''),
                                'owner_is_verified': reply_owner.get('is_verified', False),
                                'parent_comment_id': comment['instagram_id'],  # Link to parent comment
                                'reply_count': 0  # Replies don't have their own replies
                            }
                            comments.append(reply)
                
        except Exception as e:
            self.logger.error(f"Error extracting comments data: {e}")
        
        return comments
    
    def _update_profile_analytics(self, username: str):
        """Update profile analytics based on collected data"""
        try:
            profile = db.session.query(Profile).filter_by(username=username).first()
            if profile:
                # Calculate analytics
                total_posts = db.session.query(MediaPost).filter_by(username=username).count()
                total_stories = db.session.query(Story).filter_by(username=username).count()
                total_highlights = db.session.query(Highlight).filter_by(username=username).count()
                
                # Update profile
                profile.total_posts_tracked = total_posts
                profile.total_stories_tracked = total_stories
                profile.total_highlights = total_highlights
                
                # Calculate engagement rate
                if profile.follower_count > 0:
                    recent_posts = db.session.query(MediaPost).filter_by(username=username).limit(10).all()
                    if recent_posts:
                        avg_engagement = sum(post.engagement_count for post in recent_posts) / len(recent_posts)
                        profile.avg_engagement_rate = (avg_engagement / profile.followers_count) * 100
                
                db.session.commit()
                
        except Exception as e:
            self.logger.error(f"Error updating profile analytics for {username}: {e}")
    
    def _extract_user_data(self, api_response: dict) -> dict:
        """Extract user data from Star API response"""
        try:
            if 'response' in api_response and 'body' in api_response['response']:
                user_data = api_response['response']['body']['data']['user']
                return {
                    'user_id': str(user_data.get('id', '')),
                    'full_name': user_data.get('full_name', ''),
                    'biography': user_data.get('biography', ''),
                    'follower_count': user_data.get('edge_followed_by', {}).get('count', 0),
                    'following_count': user_data.get('edge_follow', {}).get('count', 0),
                    'media_count': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                    'is_verified': user_data.get('is_verified', False),
                    'is_private': user_data.get('is_private', False),
                    'is_business_account': user_data.get('is_business_account', False),
                    'profile_pic_url': user_data.get('profile_pic_url', ''),
                    'external_url': user_data.get('external_url', ''),
                    'category': user_data.get('category_name', ''),
                    'business_category': user_data.get('business_category_name', '')
                }
        except Exception as e:
            self.logger.error(f"Error extracting user data: {e}")
        return {}
    
    def _extract_media_data(self, api_response: dict) -> list:
        """Extract media data from Star API response"""
        media_items = []
        try:
            if 'response' in api_response and 'body' in api_response['response']:
                body = api_response['response']['body']
                
                # Try new format first (items array)
                if 'items' in body and isinstance(body['items'], list):
                    items = body['items']
                    self.logger.info(f"Found {len(items)} media items in new format")
                    
                    for item in items:
                        # Extract hashtags and mentions from caption
                        caption_text = item.get('caption', {}).get('text', '') if item.get('caption') else ''
                        hashtags = re.findall(r'#(\w+)', caption_text)
                        mentions = re.findall(r'@(\w+)', caption_text)
                        
                        media_item = {
                            'id': item.get('id'),
                            'shortcode': item.get('code'),
                            'link': f"https://instagram.com/p/{item.get('code')}/",
                            'media_type': self._get_media_type_from_item(item),
                            'is_video': item.get('media_type') == 2,  # 1=image, 2=video, 8=carousel
                            'carousel_media_count': len(item.get('carousel_media', [])) if item.get('carousel_media') else 1,
                            'caption': caption_text,
                            'hashtags': hashtags,
                            'mentions': mentions,
                            'post_datetime_ist': datetime.fromtimestamp(item.get('taken_at', 0)),
                            'like_count': item.get('like_count', 0),
                            'comment_count': item.get('comment_count', 0),
                            'play_count': item.get('play_count', 0),
                            'video_view_count': item.get('view_count', 0),
                            'location_name': item.get('location', {}).get('name') if item.get('location') else None,
                            'location_id': str(item.get('location', {}).get('pk')) if item.get('location') else None,
                            'display_url': item.get('display_url') or item.get('image_versions2', {}).get('candidates', [{}])[0].get('url'),
                            'raw_data': item
                        }
                        media_items.append(media_item)
                
                # Fallback to old format (edges)
                elif 'data' in body and 'user' in body['data']:
                    edges = body['data']['user']['edge_owner_to_timeline_media']['edges']
                    self.logger.info(f"Found {len(edges)} media items in old format")
                    
                    for edge in edges:
                        node = edge['node']
                        
                        # Extract hashtags and mentions from caption
                        caption = node.get('edge_media_to_caption', {}).get('edges', [])
                        caption_text = caption[0]['node']['text'] if caption else ''
                        hashtags = re.findall(r'#(\w+)', caption_text)
                        mentions = re.findall(r'@(\w+)', caption_text)
                        
                        media_item = {
                            'id': node.get('id'),
                            'shortcode': node.get('shortcode'),
                            'link': f"https://instagram.com/p/{node.get('shortcode')}/",
                            'media_type': self._get_media_type(node),
                            'is_video': node.get('is_video', False),
                            'carousel_media_count': len(node.get('edge_sidecar_to_children', {}).get('edges', [])),
                            'caption': caption_text,
                            'hashtags': hashtags,
                            'mentions': mentions,
                            'post_datetime_ist': datetime.fromtimestamp(node.get('taken_at_timestamp', 0)),
                            'like_count': node.get('edge_media_preview_like', {}).get('count', 0),
                            'comment_count': node.get('edge_media_to_comment', {}).get('count', 0),
                            'play_count': node.get('video_play_count', 0),
                            'video_view_count': node.get('video_view_count', 0),
                            'location_name': node.get('location', {}).get('name') if node.get('location') else None,
                            'location_id': str(node.get('location', {}).get('id')) if node.get('location') else None,
                            'display_url': node.get('display_url') or node.get('display_resources', [{}])[0].get('src'),
                            'raw_data': node
                        }
                        media_items.append(media_item)
                else:
                    self.logger.warning(f"Unknown media response format. Body keys: {list(body.keys())}")
                    
        except Exception as e:
            self.logger.error(f"Error extracting media data: {e}")
        
        return media_items
    
    def _extract_story_data(self, api_response: dict) -> list:
        """Extract story data from Star API response"""
        # Implementation for story data extraction
        return []  # Placeholder
    
    def _extract_highlight_data(self, api_response: dict) -> list:
        """Extract highlight data from Star API response"""
        # Implementation for highlight data extraction
        return []  # Placeholder
    
    def _extract_follower_data(self, api_response: dict) -> list:
        """Extract follower data from Star API response"""
        # Implementation for follower data extraction
        return []  # Placeholder
    
    def _extract_similar_accounts_data(self, api_response: dict) -> list:
        """Extract similar accounts data from Star API response"""
        # Implementation for similar accounts data extraction
        return []  # Placeholder
    
    def _get_media_type(self, node: dict) -> str:
        """Determine media type from node data"""
        if node.get('__typename') == 'GraphVideo':
            return 'video'
        elif node.get('__typename') == 'GraphSidecar':
            return 'carousel_album'
        else:
            return 'image'
    
    def _get_media_type_from_item(self, item: dict) -> str:
        """Determine media type from item data (new format)"""
        media_type = item.get('media_type', 1)
        if media_type == 2:
            return 'video'
        elif media_type == 8:
            return 'carousel_album'
        else:
            return 'image'
    
    def _log_collection(self, data_type: str, username: str, status: str, 
                       records_collected: int, response_time_ms: int = 0, 
                       error_message: str = ""):
        """Log data collection activity"""
        try:
            log_entry = ApiRequestLog(
                username=username,
                endpoint=f"star_api_{data_type}",
                status=status,
                response_time_ms=response_time_ms,
                error_message=error_message
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            self.logger.error(f"Error logging collection activity: {e}")

# Factory function for service creation
def create_star_api_data_service(api_key: str) -> StarApiDataService:
    """Factory function to create StarApiDataService instance"""
    return StarApiDataService(api_key)
