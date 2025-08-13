"""
Enhanced Star API Service for Instagram Analytics
Supports comprehensive data collection from Star API endpoints
"""
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import pytz
from models.database import db, Profile, MediaPost, Story, DailyMetrics
from sqlalchemy import func, desc, and_
import logging

# Timezone setup
IST = pytz.timezone("Asia/Kolkata")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StarAPIService:
    """
    Comprehensive Instagram data collection service using Star API
    """
    
    def __init__(self, api_key: str, base_url: str = "https://starapi1.p.rapidapi.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "starapi1.p.rapidapi.com",
            "Content-Type": "application/json",
        }
        
        # API Endpoints (Updated with correct POST endpoints)
        self.endpoints = {
            # User related
            'user_info_by_username': f"{base_url}/instagram/user/get_web_profile_info",
            'user_info_by_id': f"{base_url}/instagram/user/get_info_by_id",
            'user_about': f"{base_url}/instagram/user/get_about",
            'user_media': f"{base_url}/instagram/user/get_media",
            'user_clips': f"{base_url}/instagram/user/get_clips",
            'user_guides': f"{base_url}/instagram/user/get_guides",
            'user_tags': f"{base_url}/instagram/user/get_tags",
            'user_followers': f"{base_url}/instagram/user/get_followers",
            'user_following': f"{base_url}/instagram/user/get_following",
            'user_stories': f"{base_url}/instagram/user/get_stories",
            'user_highlights': f"{base_url}/instagram/user/get_highlights",
            'user_live': f"{base_url}/instagram/user/get_live",
            'user_similar_accounts': f"{base_url}/instagram/user/get_similar_accounts",
            
            # Media related
            'media_info': f"{base_url}/instagram/media/get_media_info",
            'media_info_by_shortcode': f"{base_url}/instagram/media/get_media_info_by_shortcode",
            'media_likes': f"{base_url}/instagram/media/get_media_likes",
            'media_comments': f"{base_url}/instagram/media/get_media_comments",
            'media_shortcode_by_id': f"{base_url}/instagram/media/get_shortcode_by_id",
            'media_id_by_shortcode': f"{base_url}/instagram/media/get_id_by_shortcode",
            
            # Other endpoints
            'guide_info': f"{base_url}/instagram/guide/get_guide_info",
            'location_info': f"{base_url}/instagram/location/get_location_info",
            'location_media': f"{base_url}/instagram/location/get_location_media",
            'hashtag_info': f"{base_url}/instagram/hashtag/get_hashtag_info",
            'hashtag_media': f"{base_url}/instagram/hashtag/get_hashtag_media",
            'highlight_stories': f"{base_url}/instagram/highlights/get_highlight_stories",
            'comment_likes': f"{base_url}/instagram/comment/get_comment_likes",
            'comment_replies': f"{base_url}/instagram/comment/get_comment_replies",
            'audio_media': f"{base_url}/instagram/audio/get_audio_media",
            'live_info': f"{base_url}/instagram/live/get_live_info",
        }
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any], max_retries: int = 3) -> Optional[Dict]:
        """
        Make API request with error handling and retries
        """
        for attempt in range(max_retries):
            try:
                response = requests.post(endpoint, json=payload, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if data.get("status") == "done":
                    return data
                else:
                    logger.warning(f"API returned status: {data.get('status')} for endpoint: {endpoint}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All retries failed for endpoint: {endpoint}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None
        
        return None
    
    def get_user_info_by_username(self, username: str) -> Optional[Dict]:
        """Get user info by username"""
        payload = {"username": username}
        return self._make_request(self.endpoints['user_info_by_username'], payload)
    
    def get_user_info_by_id(self, user_id: Union[str, int]) -> Optional[Dict]:
        """Get user info by user ID"""
        payload = {"id": int(user_id)}
        return self._make_request(self.endpoints['user_info_by_id'], payload)
    
    def get_user_about(self, user_id: Union[str, int]) -> Optional[Dict]:
        """Get user about information"""
        payload = {"id": int(user_id)}
        return self._make_request(self.endpoints['user_about'], payload)
    
    def get_user_media(self, user_id: Union[str, int], count: int = 50) -> Optional[Dict]:
        """Get user media posts by user ID"""
        payload = {"id": int(user_id), "count": count}
        return self._make_request(self.endpoints['user_media'], payload)
    
    def get_user_clips(self, user_id: Union[str, int], count: int = 50) -> Optional[Dict]:
        """Get user clips/reels by user ID"""
        payload = {"id": int(user_id), "count": count}
        return self._make_request(self.endpoints['user_clips'], payload)
    
    def get_user_guides(self, user_id: Union[str, int]) -> Optional[Dict]:
        """Get user guides by user ID"""
        payload = {"id": int(user_id)}
        return self._make_request(self.endpoints['user_guides'], payload)
    
    def get_user_tags(self, user_id: Union[str, int], count: int = 50) -> Optional[Dict]:
        """Get user tagged media by user ID"""
        payload = {"id": int(user_id), "count": count}
        return self._make_request(self.endpoints['user_tags'], payload)
    
    def get_user_followers(self, user_id: Union[str, int], count: int = 50) -> Optional[Dict]:
        """Get user followers by user ID"""
        payload = {"id": int(user_id), "count": count}
        return self._make_request(self.endpoints['user_followers'], payload)
    
    def get_user_following(self, user_id: Union[str, int], count: int = 50) -> Optional[Dict]:
        """Get user following by user ID"""
        payload = {"id": int(user_id), "count": count}
        return self._make_request(self.endpoints['user_following'], payload)
    
    def get_user_stories(self, user_id: Union[str, int]) -> Optional[Dict]:
        """Get user stories by user ID - uses ids array format"""
        payload = {"ids": [int(user_id)]}
        return self._make_request(self.endpoints['user_stories'], payload)
    
    def get_user_highlights(self, user_id: Union[str, int]) -> Optional[Dict]:
        """Get user highlights by user ID"""
        payload = {"id": int(user_id)}
        return self._make_request(self.endpoints['user_highlights'], payload)
    
    def get_user_live(self, user_id: Union[str, int]) -> Optional[Dict]:
        """Get user live streams by user ID"""
        payload = {"id": int(user_id)}
        return self._make_request(self.endpoints['user_live'], payload)
    
    def get_media_info(self, media_id: str) -> Optional[Dict]:
        """Get media info by media ID"""
        payload = {"media_id": media_id}
        return self._make_request(self.endpoints['media_info'], payload)
    
    def get_media_comments(self, media_id: str, count: int = 100) -> Optional[Dict]:
        """Get media comments"""
        payload = {"media_id": media_id, "count": count}
        return self._make_request(self.endpoints['media_comments'], payload)
    
    def get_media_likes(self, media_id: str, count: int = 100) -> Optional[Dict]:
        """Get media likes"""
        payload = {"media_id": media_id, "count": count}
        return self._make_request(self.endpoints['media_likes'], payload)
    
    def get_hashtag_info(self, hashtag: str) -> Optional[Dict]:
        """Get hashtag info"""
        payload = {"hashtag": hashtag}
        return self._make_request(self.endpoints['hashtag_info'], payload)
    
    def get_hashtag_media(self, hashtag: str, count: int = 50) -> Optional[Dict]:
        """Get hashtag media"""
        payload = {"hashtag": hashtag, "count": count}
        return self._make_request(self.endpoints['hashtag_media'], payload)
    
    def save_profile_data(self, username: str, profile_data: Dict) -> bool:
        """
        Save profile data to database with enhanced fields
        """
        try:
            if not profile_data or 'response' not in profile_data:
                return False
            
            user_data = profile_data['response']['body']['data']['user']
            
            # Check if profile exists
            profile = Profile.query.filter_by(username=username).first()
            if not profile:
                profile = Profile(username=username)
            
            # Update profile fields
            profile.full_name = user_data.get('full_name', '')
            profile.biography = user_data.get('biography', '')
            profile.follower_count = user_data.get('edge_followed_by', {}).get('count', 0)
            profile.following_count = user_data.get('edge_follow', {}).get('count', 0)
            profile.media_count = user_data.get('edge_owner_to_timeline_media', {}).get('count', 0)
            profile.is_verified = user_data.get('is_verified', False)
            profile.is_private = user_data.get('is_private', False)
            profile.profile_pic_url = user_data.get('profile_pic_url_hd', '')
            profile.last_updated = datetime.now(IST)
            
            db.session.merge(profile)
            db.session.commit()
            
            logger.info(f"Profile data saved for {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving profile data for {username}: {e}")
            db.session.rollback()
            return False
    
    def save_media_data(self, username: str, media_data: Dict) -> int:
        """
        Save media data to database with enhanced fields
        """
        saved_count = 0
        
        try:
            if not media_data or 'response' not in media_data:
                return 0
            
            media_items = media_data['response']['body']['data']['user']['edge_owner_to_timeline_media']['edges']
            
            for item in media_items:
                node = item['node']
                media_id = node.get('id', '')
                
                if not media_id:
                    continue
                
                # Check if media already exists
                existing_media = MediaPost.query.filter_by(id=media_id).first()
                if existing_media:
                    continue  # Skip existing media
                
                # Determine media type
                media_type = 'post'
                if node.get('is_video'):
                    media_type = 'reel' if node.get('product_type') == 'clips' else 'video'
                elif node.get('__typename') == 'GraphSidecar':
                    media_type = 'carousel'
                
                # Create new media post
                media_post = MediaPost(
                    id=media_id,
                    username=username,
                    og_username=username,
                    link=f"https://www.instagram.com/p/{node.get('shortcode', '')}/",
                    media_type=media_type,
                    is_video=node.get('is_video', False),
                    carousel_media_count=len(node.get('edge_sidecar_to_children', {}).get('edges', [])),
                    caption=self._extract_caption(node),
                    post_datetime_ist=datetime.fromtimestamp(node.get('taken_at_timestamp', 0), IST),
                    like_count=node.get('edge_media_preview_like', {}).get('count', 0),
                    comment_count=node.get('edge_media_to_comment', {}).get('count', 0),
                    play_count=node.get('video_view_count', 0),
                    raw_data=node
                )
                
                db.session.add(media_post)
                saved_count += 1
            
            db.session.commit()
            logger.info(f"Saved {saved_count} media posts for {username}")
            
        except Exception as e:
            logger.error(f"Error saving media data for {username}: {e}")
            db.session.rollback()
        
        return saved_count
    
    def save_stories_data(self, username: str, stories_data: Dict) -> int:
        """
        Save stories data to database
        """
        saved_count = 0
        
        try:
            if not stories_data or 'response' not in stories_data:
                return 0
            
            stories = stories_data['response']['body']['data']['user']['story']['edges']
            
            for story_item in stories:
                story = story_item['node']
                story_id = story.get('id', '')
                
                if not story_id:
                    continue
                
                # Check if story already exists
                existing_story = Story.query.filter_by(story_id=story_id).first()
                if existing_story:
                    continue
                
                # Create new story
                story_obj = Story(
                    story_id=story_id,
                    username=username,
                    og_username=username,
                    media_type='video' if story.get('is_video') else 'photo',
                    post_datetime_ist=datetime.fromtimestamp(story.get('taken_at_timestamp', 0), IST),
                    expire_datetime_ist=datetime.fromtimestamp(story.get('expiring_at_timestamp', 0), IST),
                    raw_data=story
                )
                
                db.session.add(story_obj)
                saved_count += 1
            
            db.session.commit()
            logger.info(f"Saved {saved_count} stories for {username}")
            
        except Exception as e:
            logger.error(f"Error saving stories data for {username}: {e}")
            db.session.rollback()
        
        return saved_count
    
    def _extract_caption(self, node: Dict) -> str:
        """Extract caption from media node"""
        try:
            edges = node.get('edge_media_to_caption', {}).get('edges', [])
            if edges:
                return edges[0]['node']['text']
        except:
            pass
        return ''
    
    def collect_comprehensive_data(self, username: str) -> Dict[str, Any]:
        """
        Collect comprehensive data for a user using multiple endpoints
        """
        results = {
            'username': username,
            'success': False,
            'data_collected': {},
            'errors': []
        }
        
        try:
            # 1. Get user profile info
            logger.info(f"Collecting profile data for {username}")
            profile_data = self.get_user_info_by_username(username)
            if profile_data:
                self.save_profile_data(username, profile_data)
                results['data_collected']['profile'] = True
                
                # 2. Extract user_id for subsequent calls
                try:
                    user_id = profile_data['data']['response']['body']['data']['user']['id']
                    logger.info(f"Extracted user_id: {user_id} for {username}")
                except (KeyError, TypeError):
                    results['errors'].append("Failed to extract user_id from profile")
                    return results
                
                # 3. Get user media using user_id
                logger.info(f"Collecting media data for {username}")
                media_data = self.get_user_media(user_id, count=100)
                if media_data:
                    media_count = self.save_media_data(username, media_data)
                    results['data_collected']['media'] = media_count
                else:
                    results['errors'].append("Failed to get media data")
                
                # 4. Get user clips/reels using user_id
                logger.info(f"Collecting clips data for {username}")
                clips_data = self.get_user_clips(user_id, count=50)
                if clips_data:
                    results['data_collected']['clips'] = True
                else:
                    results['errors'].append("Failed to get clips data")
                
                # 5. Get user stories using user_id
                logger.info(f"Collecting stories data for {username}")
                stories_data = self.get_user_stories(user_id)
                if stories_data:
                    stories_count = self.save_stories_data(username, stories_data)
                    results['data_collected']['stories'] = stories_count
                else:
                    results['errors'].append("Failed to get stories data")
                
                # 6. Get user highlights using user_id
                logger.info(f"Collecting highlights data for {username}")
                highlights_data = self.get_user_highlights(user_id)
                if highlights_data:
                    results['data_collected']['highlights'] = True
                else:
                    results['errors'].append("Failed to get highlights data")
            else:
                results['errors'].append("Failed to get profile data")
                
        except Exception as e:
            logger.error(f"Error in comprehensive data collection for {username}: {e}")
            results['errors'].append(str(e))
        
        results['success'] = len(results['data_collected']) > 0
        
        return results
    
    # Additional endpoints for comprehensive Instagram data
    def get_similar_accounts(self, user_id: Union[str, int]) -> Optional[Dict]:
        """Get similar accounts by user ID"""
        payload = {"id": int(user_id)}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/user/get_similar_accounts", payload)
    
    def search_users(self, query: str) -> Optional[Dict]:
        """Search for users by query"""
        payload = {"query": query}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/user/search", payload)
    
    def get_location_info(self, location_id: Union[str, int]) -> Optional[Dict]:
        """Get location info by location ID"""
        payload = {"id": int(location_id)}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/location/get_info", payload)
    
    def get_location_media(self, location_id: Union[str, int], tab: str = "ranked") -> Optional[Dict]:
        """Get location media by location ID"""
        payload = {"id": int(location_id), "tab": tab}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/location/get_media", payload)
    
    def search_locations(self, query: str) -> Optional[Dict]:
        """Search for locations by query"""
        payload = {"query": query}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/location/search", payload)
    
    def get_hashtag_info_by_name(self, name: str) -> Optional[Dict]:
        """Get hashtag info by hashtag name"""
        payload = {"name": name}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/hashtag/get_info", payload)
    
    def get_hashtag_media_by_name(self, name: str, tab: str = "top") -> Optional[Dict]:
        """Get hashtag media by hashtag name"""
        payload = {"name": name, "tab": tab}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/hashtag/get_media", payload)
    
    def get_highlight_stories(self, highlight_ids: list) -> Optional[Dict]:
        """Get stories from highlights by highlight IDs"""
        payload = {"ids": highlight_ids}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/highlight/get_stories", payload)
    
    def get_comment_likes(self, comment_id: str) -> Optional[Dict]:
        """Get likes on a comment by comment ID"""
        payload = {"id": comment_id}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/comment/get_likes", payload)
    
    def get_comment_replies(self, comment_id: str, media_id: str) -> Optional[Dict]:
        """Get replies to a comment"""
        payload = {"id": comment_id, "media_id": media_id}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/comment/get_replies", payload)
    
    def get_audio_media(self, audio_id: str) -> Optional[Dict]:
        """Get media using a specific audio by audio ID"""
        payload = {"id": audio_id}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/audio/get_media", payload)
    
    def search_audio(self, query: str) -> Optional[Dict]:
        """Search for audio by query"""
        payload = {"query": query}
        return self._make_request("https://starapi1.p.rapidapi.com/instagram/audio/search", payload)

    def test_all_endpoints(self, test_username: str = "instagram") -> Dict[str, Any]:
        """
        Test all available endpoints with a sample username
        """
        test_results = {
            'test_username': test_username,
            'timestamp': datetime.now(IST).isoformat(),
            'endpoint_results': {},
            'summary': {
                'total_endpoints': len(self.endpoints),
                'successful': 0,
                'failed': 0
            }
        }
        
        # Test user-related endpoints
        user_endpoints = [
            ('user_info_by_username', lambda: self.get_user_info_by_username(test_username)),
            ('user_media', lambda: self.get_user_media(test_username, count=10)),
            ('user_clips', lambda: self.get_user_clips(test_username, count=10)),
            ('user_stories', lambda: self.get_user_stories(test_username)),
            ('user_highlights', lambda: self.get_user_highlights(test_username)),
        ]
        
        for endpoint_name, endpoint_func in user_endpoints:
            try:
                logger.info(f"Testing endpoint: {endpoint_name}")
                result = endpoint_func()
                
                if result:
                    test_results['endpoint_results'][endpoint_name] = {
                        'status': 'success',
                        'data_size': len(str(result)),
                        'has_data': bool(result.get('response', {}).get('body', {}).get('data'))
                    }
                    test_results['summary']['successful'] += 1
                else:
                    test_results['endpoint_results'][endpoint_name] = {
                        'status': 'failed',
                        'error': 'No data returned'
                    }
                    test_results['summary']['failed'] += 1
                
                # Add small delay between requests
                time.sleep(1)
                
            except Exception as e:
                test_results['endpoint_results'][endpoint_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                test_results['summary']['failed'] += 1
        
        return test_results

# Initialize service instance (will be used by other modules)
def create_star_api_service(api_key: str) -> StarAPIService:
    """Factory function to create StarAPIService instance"""
    return StarAPIService(api_key)
