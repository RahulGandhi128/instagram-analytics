"""
Profile Management Endpoints - Add, delete, get profiles and data fetching
"""
from flask import Blueprint, request, jsonify
from services.star_api_data_service import create_star_api_data_service
from models.database import db, Profile, MediaPost
from sqlalchemy import func, desc
from datetime import datetime
import pytz
import os

profiles_bp = Blueprint('profiles', __name__)
IST = pytz.timezone("Asia/Kolkata")

@profiles_bp.route('/profiles', methods=['POST'])
def add_profile():
    """
    Add a new profile to track
    """
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username is required'
            }), 400

        # Check if profile already exists
        existing_profile = Profile.query.filter_by(username=username).first()
        if existing_profile:
            return jsonify({
                'success': False,
                'error': 'Profile already exists'
            }), 409

        # Create new profile
        profile = Profile(username=username)
        db.session.add(profile)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {'username': username}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/profiles/<username>', methods=['DELETE'])
def delete_profile(username):
    """
    Delete a profile and all associated data
    """
    try:
        # Find the profile
        profile = Profile.query.filter_by(username=username).first()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404

        # Delete associated data
        MediaPost.query.filter_by(profile_id=profile.id).delete()
        Story.query.filter_by(profile_id=profile.id).delete()
        
        # Delete the profile
        db.session.delete(profile)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Profile {username} deleted successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/profiles', methods=['GET'])
def get_profiles():
    """
    Get all tracked profiles with their stats
    """
    try:
        profiles = Profile.query.all()
        
        profile_data = []
        for profile in profiles:
            media_count = MediaPost.query.filter_by(username=profile.username).count()
            story_count = Story.query.filter_by(username=profile.username).count()
            
            # Get latest media for thumbnail
            latest_media = MediaPost.query.filter_by(username=profile.username)\
                                         .order_by(desc(MediaPost.post_datetime_ist))\
                                         .first()
            
            profile_data.append({
                'username': profile.username,
                'user_id': profile.user_id,
                'full_name': profile.full_name,
                'biography': profile.biography,
                'follower_count': profile.follower_count,
                'following_count': profile.following_count,
                'media_count': profile.media_count or media_count,
                'story_count': story_count,
                'is_verified': profile.is_verified,
                'is_private': profile.is_private,
                'is_business_account': profile.is_business_account,
                'profile_pic_url': profile.profile_pic_url,
                'external_url': profile.external_url,
                'category': profile.category,
                'avg_engagement_rate': profile.avg_engagement_rate,
                'total_posts_tracked': profile.total_posts_tracked,
                'latest_media_shortcode': latest_media.shortcode if latest_media else None,
                'latest_media_url': f"https://instagram.com/p/{latest_media.shortcode}/" if latest_media and latest_media.shortcode else None,
                'last_updated': profile.last_updated.isoformat() if profile.last_updated else None
            })
        
        return jsonify({
            'success': True,
            'data': profile_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/fetch-data', methods=['POST'])
def fetch_data():
    """
    Fetch Instagram data for specified usernames
    """
    try:
        data = request.get_json()
        usernames = data.get('usernames', [])
        
        if not usernames:
            return jsonify({
                'success': False,
                'error': 'No usernames provided'
            }), 400

        results = []
        for username in usernames:
            try:
                # Use Star API data service for comprehensive data collection
                api_key = os.getenv('API_KEY')
                if not api_key:
                    raise ValueError("API key not found")
                star_api_service = create_star_api_data_service(api_key)
                result = star_api_service.collect_comprehensive_data(username)
                results.append({
                    'username': username,
                    'success': True,
                    'data': result
                })
            except Exception as e:
                results.append({
                    'username': username,
                    'success': False,
                    'error': str(e)
                })

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/fetch-instagram-data', methods=['POST'])
def fetch_instagram_data():
    """
    Fetch Instagram data for all profiles or specified ones
    """
    try:
        data = request.get_json()
        usernames = data.get('usernames', [])
        
        if usernames:
            # Fetch data for specified usernames
            results = {}
            for username in usernames:
                try:
                    # Use Star API data service for comprehensive data collection
                    api_key = os.getenv('API_KEY')
                    if not api_key:
                        raise ValueError("API key not found")
                    star_api_service = create_star_api_data_service(api_key)
                    result = star_api_service.collect_comprehensive_data(username)
                    results[username] = result
                except Exception as e:
                    results[username] = {'error': str(e)}
        else:
            # Fetch data for all profiles
            profiles = Profile.query.all()
            results = {}
            for profile in profiles:
                try:
                    # Use Star API data service for comprehensive data collection
                    api_key = os.getenv('API_KEY')
                    if not api_key:
                        raise ValueError("API key not found")
                    star_api_service = create_star_api_data_service(api_key)
                    result = star_api_service.collect_comprehensive_data(profile.username)
                    results[profile.username] = result
                except Exception as e:
                    results[profile.username] = {'error': str(e)}

        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/fetch-instagram-data/<username>', methods=['POST'])
def fetch_instagram_data_for_user(username):
    """
    Fetch Instagram data for a specific user using Star API
    """
    try:
        # Use Star API data service for comprehensive data collection
        api_key = os.getenv('API_KEY')
        if not api_key:
            raise ValueError("API key not found")
        star_api_service = create_star_api_data_service(api_key)
        result = star_api_service.collect_comprehensive_data(username)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/profiles/<username>', methods=['GET'])
def get_profile(username):
    """
    Get specific profile data
    """
    try:
        profile = Profile.query.filter_by(username=username).first()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'username': profile.username,
                'bio': profile.bio,
                'follower_count': profile.follower_count,
                'following_count': profile.following_count,
                'profile_pic_url': profile.profile_pic_url
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/media', methods=['GET'])
def get_media():
    """
    Get media posts with enhanced Instagram-like data display
    """
    try:
        username = request.args.get('username')
        if not username:
            # Return empty data instead of error to stop 400 spam in logs
            return jsonify({
                'success': True,
                'data': [],
                'message': 'No username provided - returning empty results'
            }), 200
            
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        limit = request.args.get('limit', per_page, type=int)
        media_type = request.args.get('media_type')
        sort_by = request.args.get('sort_by', 'date')  # date, engagement, likes
        
        # Check if profile exists
        profile = Profile.query.filter_by(username=username).first()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        # Build query using username
        query = MediaPost.query.filter_by(username=username)
        
        # Filter by media type if specified
        if media_type:
            query = query.filter_by(media_type=media_type)
        
        # Apply sorting
        if sort_by == 'engagement':
            # Sort by total engagement using SQL COALESCE to handle NULL values
            from sqlalchemy import func
            engagement_expr = (
                func.coalesce(MediaPost.like_count, 0) +
                func.coalesce(MediaPost.comment_count, 0) +
                func.coalesce(MediaPost.save_count, 0) +
                func.coalesce(MediaPost.share_count, 0)
            )
            query = query.order_by(desc(engagement_expr))
        elif sort_by == 'likes':
            query = query.order_by(desc(MediaPost.like_count))
        else:  # default to date
            query = query.order_by(desc(MediaPost.post_datetime_ist))
        
        # Apply limit and get results
        media_posts = query.limit(limit).all()
        
        # Transform data to Instagram-like format
        posts_data = []
        for post in media_posts:
            # Calculate engagement metrics
            total_likes = post.like_count or 0
            total_comments = post.comment_count or 0
            total_saves = post.save_count or 0
            total_shares = post.share_count or 0
            total_engagement = total_likes + total_comments + total_saves + total_shares
            
            # Calculate engagement rate if follower count is available
            engagement_rate = 0
            if profile.follower_count and profile.follower_count > 0:
                engagement_rate = (total_engagement / profile.follower_count) * 100
            
            # Format post datetime safely
            post_time_ago = ""
            if post.post_datetime_ist:
                try:
                    time_diff = datetime.now(IST) - post.post_datetime_ist
                    if time_diff.days > 0:
                        post_time_ago = f"{time_diff.days}d ago"
                    elif time_diff.seconds > 3600:
                        post_time_ago = f"{time_diff.seconds // 3600}h ago"
                    else:
                        post_time_ago = f"{time_diff.seconds // 60}m ago"
                except:
                    post_time_ago = "Unknown"
            
            # Extract hashtags and mentions from caption
            hashtags = post.hashtags or []
            mentions = post.mentions or []
            
            # Determine media icon based on type
            media_icon = "📷"  # default photo
            if post.is_video:
                media_icon = "🎥"
            elif post.media_type == 'reel':
                media_icon = "🎬"
            elif post.carousel_media_count and post.carousel_media_count > 1:
                media_icon = "🖼️"
            
            post_data = {
                'id': post.id,
                'username': post.username,
                'og_username': post.og_username or post.username,
                'full_name': post.full_name or profile.full_name,
                'shortcode': post.shortcode,
                'instagram_url': f"https://instagram.com/p/{post.shortcode}/" if post.shortcode else None,
                'media_type': post.media_type or 'post',
                'media_icon': media_icon,
                'is_video': post.is_video or False,
                'carousel_media_count': post.carousel_media_count or 1,
                'is_carousel': (post.carousel_media_count or 1) > 1,
                
                # Content
                'caption': post.caption,
                'caption_preview': post.caption[:100] + "..." if post.caption and len(post.caption) > 100 else post.caption,
                'hashtags': hashtags,
                'hashtags_count': len(hashtags),
                'mentions': mentions,
                'mentions_count': len(mentions),
                
                # Timing
                'post_datetime_ist': post.post_datetime_ist.isoformat() if post.post_datetime_ist else None,
                'post_date': post.post_datetime_ist.strftime('%Y-%m-%d') if post.post_datetime_ist else None,
                'post_time': post.post_datetime_ist.strftime('%H:%M') if post.post_datetime_ist else None,
                'post_time_ago': post_time_ago,
                'post_day_of_week': post.post_datetime_ist.strftime('%A') if post.post_datetime_ist else None,
                
                # Engagement metrics
                'like_count': total_likes,
                'comment_count': total_comments,
                'save_count': total_saves,
                'share_count': total_shares,
                'reshare_count': post.reshare_count or 0,
                'play_count': post.play_count or 0,
                'video_view_count': post.video_view_count or 0,
                'total_engagement': total_engagement,
                'engagement_rate': round(engagement_rate, 2),
                
                # Formatted engagement for display
                'like_count_formatted': _format_count(total_likes),
                'comment_count_formatted': _format_count(total_comments),
                'save_count_formatted': _format_count(total_saves),
                'share_count_formatted': _format_count(total_shares),
                'total_engagement_formatted': _format_count(total_engagement),
                
                # Location
                'location_name': post.location_name,
                'location_id': post.location_id,
                'has_location': bool(post.location_name),
                
                # Content flags
                'is_collab': post.is_collab or False,
                'collab_with': post.collab_with,
                'is_ad': post.is_ad or False,
                'is_sponsored': post.is_sponsored or False,
                
                # Data quality
                'data_quality_score': post.data_quality_score or 1.0,
                'first_fetched': post.first_fetched.isoformat() if post.first_fetched else None,
                'last_updated': post.last_updated.isoformat() if post.last_updated else None,
                
                # Performance indicators
                'is_high_performing': total_engagement > (profile.avg_engagement_rate or 0) * 1.5 if profile.avg_engagement_rate else False,
                'performance_score': min(100, (engagement_rate / max(profile.avg_engagement_rate or 1, 1)) * 100) if profile.avg_engagement_rate else 0
            }
            posts_data.append(post_data)
        
        # Calculate summary statistics
        total_posts = len(posts_data)
        total_likes_sum = sum(post['like_count'] for post in posts_data)
        total_comments_sum = sum(post['comment_count'] for post in posts_data)
        total_engagement_sum = sum(post['total_engagement'] for post in posts_data)
        avg_engagement = total_engagement_sum / total_posts if total_posts > 0 else 0
        
        return jsonify({
            'success': True,
            'data': posts_data,
            'profile_info': {
                'username': profile.username,
                'full_name': profile.full_name,
                'profile_pic_url': profile.profile_pic_url,
                'follower_count': profile.follower_count,
                'following_count': profile.following_count,
                'biography': profile.biography,
                'is_verified': profile.is_verified,
                'is_private': profile.is_private,
                'is_business_account': profile.is_business_account,
                'avg_engagement_rate': profile.avg_engagement_rate
            },
            'summary_stats': {
                'total_posts_returned': total_posts,
                'total_likes': total_likes_sum,
                'total_comments': total_comments_sum,
                'total_engagement': total_engagement_sum,
                'avg_engagement_per_post': round(avg_engagement, 2),
                'likes_formatted': _format_count(total_likes_sum),
                'comments_formatted': _format_count(total_comments_sum),
                'engagement_formatted': _format_count(total_engagement_sum)
            },
            'metadata': {
                'username': username,
                'media_type_filter': media_type,
                'sort_by': sort_by,
                'limit': limit,
                'page': page,
                'per_page': per_page
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _format_count(count):
    """Format large numbers for display (e.g., 1.2K, 1.5M)"""
    if count >= 1000000:
        return f"{count/1000000:.1f}M"
    elif count >= 1000:
        return f"{count/1000:.1f}K"
    else:
        return str(count)

@profiles_bp.route('/media/<post_id>', methods=['GET'])
def get_post_details(post_id):
    """
    Get detailed information about a specific post
    """
    try:
        post = MediaPost.query.filter_by(id=post_id).first()
        if not post:
            return jsonify({
                'success': False,
                'error': 'Post not found'
            }), 404

        # Get profile information
        profile = Profile.query.filter_by(username=post.username).first()
        
        # Calculate engagement metrics
        total_likes = post.like_count or 0
        total_comments = post.comment_count or 0
        total_saves = post.save_count or 0
        total_shares = post.share_count or 0
        total_engagement = total_likes + total_comments + total_saves + total_shares
        
        # Calculate engagement rate
        engagement_rate = 0
        if profile and profile.follower_count and profile.follower_count > 0:
            engagement_rate = (total_engagement / profile.follower_count) * 100

        post_details = {
            'id': post.id,
            'username': post.username,
            'og_username': post.og_username or post.username,
            'full_name': post.full_name,
            'shortcode': post.shortcode,
            'instagram_url': f"https://instagram.com/p/{post.shortcode}/" if post.shortcode else None,
            'media_type': post.media_type,
            'is_video': post.is_video,
            'carousel_media_count': post.carousel_media_count,
            'caption': post.caption,
            'hashtags': post.hashtags or [],
            'mentions': post.mentions or [],
            'post_datetime_ist': post.post_datetime_ist.isoformat() if post.post_datetime_ist else None,
            'like_count': total_likes,
            'comment_count': total_comments,
            'save_count': total_saves,
            'share_count': total_shares,
            'reshare_count': post.reshare_count or 0,
            'play_count': post.play_count or 0,
            'video_view_count': post.video_view_count or 0,
            'total_engagement': total_engagement,
            'engagement_rate': round(engagement_rate, 2),
            'location_name': post.location_name,
            'location_id': post.location_id,
            'is_collab': post.is_collab,
            'collab_with': post.collab_with,
            'is_ad': post.is_ad,
            'is_sponsored': post.is_sponsored,
            'data_quality_score': post.data_quality_score,
            'first_fetched': post.first_fetched.isoformat() if post.first_fetched else None,
            'last_updated': post.last_updated.isoformat() if post.last_updated else None,
            'raw_data': post.raw_data  # Full raw data from API
        }

        return jsonify({
            'success': True,
            'data': post_details,
            'profile_info': {
                'username': profile.username if profile else post.username,
                'full_name': profile.full_name if profile else post.full_name,
                'profile_pic_url': profile.profile_pic_url if profile else None,
                'follower_count': profile.follower_count if profile else None,
                'is_verified': profile.is_verified if profile else False
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/analytics-summary', methods=['GET'])
def get_analytics_summary():
    """
    Get comprehensive analytics summary for display capabilities
    """
    try:
        username = request.args.get('username')
        
        # Available data structure analysis
        available_features = {
            'profile_data': {
                'available': True,
                'fields': [
                    'username', 'user_id', 'full_name', 'biography', 
                    'follower_count', 'following_count', 'media_count',
                    'is_verified', 'is_private', 'is_business_account',
                    'profile_pic_url', 'external_url', 'category',
                    'avg_engagement_rate', 'total_posts_tracked'
                ],
                'display_capabilities': [
                    'Profile header with bio and stats',
                    'Verification badge display',
                    'Business/Personal account indicator',
                    'Follower/Following counts',
                    'Average engagement rate'
                ]
            },
            'media_posts': {
                'available': True,
                'fields': [
                    'id', 'shortcode', 'caption', 'hashtags', 'mentions',
                    'post_datetime_ist', 'like_count', 'comment_count',
                    'save_count', 'share_count', 'video_view_count',
                    'media_type', 'is_video', 'carousel_media_count',
                    'location_name', 'is_collab', 'is_ad', 'is_sponsored'
                ],
                'display_capabilities': [
                    'Instagram-like post grid',
                    'Individual post detail view',
                    'Engagement metrics (likes, comments, saves, shares)',
                    'Hashtag and mention extraction',
                    'Media type indicators (photo/video/carousel)',
                    'Post timing analysis',
                    'Location tagging info',
                    'Collaboration and ad detection',
                    'Performance scoring',
                    'Sorting by engagement/date/likes'
                ]
            },
            'stories': {
                'available': True,
                'fields': [
                    'story_id', 'media_type', 'post_datetime_ist',
                    'expire_datetime_ist', 'is_paid_partnership', 'is_reel_media'
                ],
                'display_capabilities': [
                    'Story timeline view',
                    'Story type indicators',
                    'Paid partnership detection',
                    'Reel media identification'
                ],
                'limitations': [
                    'No view counts available',
                    'No story media URLs',
                    'Limited engagement data'
                ]
            },
            'analytics': {
                'available': True,
                'calculations': [
                    'Total engagement (likes + comments + saves + shares)',
                    'Engagement rate (engagement/followers * 100)',
                    'Average engagement per post',
                    'Post frequency analysis',
                    'Best performing content',
                    'Hashtag performance',
                    'Posting time optimization',
                    'Content type performance (photo vs video vs carousel)'
                ],
                'charts_possible': [
                    'Engagement over time',
                    'Post performance distribution',
                    'Hashtag cloud',
                    'Posting time heatmap',
                    'Content type breakdown',
                    'Engagement rate trends'
                ]
            }
        }
        
        # NOT available features
        not_available_features = {
            'comments_content': {
                'reason': 'Instagram API restrictions',
                'alternatives': ['Comment count only', 'Engagement metrics']
            },
            'follower_list': {
                'reason': 'Privacy restrictions',
                'alternatives': ['Follower count trends', 'Growth analytics']
            },
            'story_views': {
                'reason': 'Limited API access',
                'alternatives': ['Story count', 'Story frequency']
            },
            'dm_interactions': {
                'reason': 'Privacy restrictions',
                'alternatives': ['Public engagement metrics']
            },
            'real_time_data': {
                'reason': 'API rate limits',
                'alternatives': ['Scheduled data updates', 'Historical trends']
            }
        }

        if username:
            # Get specific user data
            profile = Profile.query.filter_by(username=username).first()
            if profile:
                media_count = MediaPost.query.filter_by(username=username).count()
                story_count = Story.query.filter_by(username=username).count()
                
                user_data = {
                    'profile_exists': True,
                    'total_posts_in_db': media_count,
                    'total_stories_in_db': story_count,
                    'data_quality': 'Good' if media_count > 0 else 'No posts available',
                    'last_updated': profile.last_updated.isoformat() if profile.last_updated else None
                }
            else:
                user_data = {
                    'profile_exists': False,
                    'message': 'Profile not found in database'
                }
        else:
            user_data = None

        return jsonify({
            'success': True,
            'data': {
                'available_features': available_features,
                'not_available_features': not_available_features,
                'user_specific_data': user_data,
                'recommended_frontend_components': [
                    'Profile header card with stats',
                    'Instagram-style post grid',
                    'Post detail modal with full metrics',
                    'Engagement analytics dashboard',
                    'Hashtag performance analyzer',
                    'Posting time optimization chart',
                    'Content performance comparison',
                    'Growth tracking charts'
                ]
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/stories', methods=['GET'])
def get_stories():
    """
    Get stories with pagination
    """
    try:
        username = request.args.get('username')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Story.query
        
        if username:
            # Filter by username directly since Story model should have username field
            query = query.filter_by(username=username)
        
        stories = query.order_by(desc(Story.id)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'stories': [{
                    'story_id': story.story_id,
                    'username': story.username,
                    'og_username': story.og_username,
                    'full_name': story.full_name,
                    'media_type': story.media_type,
                    'post_datetime_ist': story.post_datetime_ist.isoformat() if story.post_datetime_ist else None,
                    'expire_datetime_ist': story.expire_datetime_ist.isoformat() if story.expire_datetime_ist else None,
                    'is_paid_partnership': story.is_paid_partnership,
                    'is_reel_media': story.is_reel_media,
                    'first_fetched': story.first_fetched.isoformat() if story.first_fetched else None
                } for story in stories.items],
                'total': stories.total,
                'pages': stories.pages,
                'current_page': page
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
