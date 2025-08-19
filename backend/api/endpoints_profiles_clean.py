"""
Clean Instagram Analytics API Endpoints
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, func
from models.database import db, Profile, MediaPost
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

profiles_bp = Blueprint('profiles', __name__)

def _format_count(count):
    """Format large numbers for display (e.g., 1.5K, 2.3M)"""
    if count >= 1000000:
        return f"{count / 1000000:.1f}M"
    elif count >= 1000:
        return f"{count / 1000:.1f}K"
    else:
        return str(count)

@profiles_bp.route('/profiles', methods=['GET'])
def get_profiles():
    """Get all profiles"""
    try:
        profiles = Profile.query.all()
        profiles_data = []
        
        for profile in profiles:
            # Get media count
            media_count = MediaPost.query.filter_by(username=profile.username).count()
            
            # Get latest media for engagement rate calculation
            latest_media = MediaPost.query.filter_by(username=profile.username)\
                .order_by(desc(MediaPost.post_datetime_ist)).limit(10).all()
            
            profile_data = profile.to_dict()
            profile_data.update({
                'total_media_posts': media_count,
                'latest_post_count': len(latest_media)
            })
            profiles_data.append(profile_data)
        
        return jsonify({
            'success': True,
            'data': profiles_data,
            'total_profiles': len(profiles_data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/media', methods=['GET'])
def get_media():
    """Get media posts with Instagram-like formatting"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({
                'success': True,
                'data': [],
                'message': 'No username provided'
            }), 200
            
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        limit = request.args.get('limit', per_page, type=int)
        media_type = request.args.get('media_type')
        sort_by = request.args.get('sort_by', 'date')
        
        # Check if profile exists
        profile = Profile.query.filter_by(username=username).first()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        # Build query
        query = MediaPost.query.filter_by(username=username)
        
        # Filter by media type
        if media_type:
            query = query.filter_by(media_type=media_type)
        
        # Apply sorting
        if sort_by == 'engagement':
            engagement_expr = (
                func.coalesce(MediaPost.like_count, 0) +
                func.coalesce(MediaPost.comment_count, 0) +
                func.coalesce(MediaPost.save_count, 0) +
                func.coalesce(MediaPost.share_count, 0)
            )
            query = query.order_by(desc(engagement_expr))
        elif sort_by == 'likes':
            query = query.order_by(desc(MediaPost.like_count))
        else:
            query = query.order_by(desc(MediaPost.post_datetime_ist))
        
        # Get results
        media_posts = query.limit(limit).all()
        
        # Format data
        posts_data = []
        for post in media_posts:
            # Calculate metrics
            total_likes = post.like_count or 0
            total_comments = post.comment_count or 0
            total_saves = post.save_count or 0
            total_shares = post.share_count or 0
            total_engagement = total_likes + total_comments + total_saves + total_shares
            
            # Calculate engagement rate
            engagement_rate = 0
            if profile.follower_count and profile.follower_count > 0:
                engagement_rate = (total_engagement / profile.follower_count) * 100
            
            # Format time
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
            
            # Media icon
            media_icon = "📷"
            if post.is_video:
                media_icon = "🎥"
            elif post.media_type == 'reel':
                media_icon = "🎬"
            elif post.carousel_media_count and post.carousel_media_count > 1:
                media_icon = "🖼️"
            
            post_data = {
                'id': post.id,
                'username': post.username,
                'shortcode': post.shortcode,
                'instagram_url': f"https://instagram.com/p/{post.shortcode}/" if post.shortcode else post.link,
                'media_type': post.media_type or 'post',
                'media_icon': media_icon,
                'is_video': post.is_video or False,
                'carousel_media_count': post.carousel_media_count or 1,
                'is_carousel': (post.carousel_media_count or 1) > 1,
                
                # Content
                'caption': post.caption,
                'caption_preview': post.caption[:100] + "..." if post.caption and len(post.caption) > 100 else post.caption,
                'hashtags': post.hashtags or [],
                'hashtags_count': len(post.hashtags or []),
                'mentions': post.mentions or [],
                'mentions_count': len(post.mentions or []),
                
                # Timing
                'post_datetime_ist': post.post_datetime_ist.isoformat() if post.post_datetime_ist else None,
                'post_date': post.post_datetime_ist.strftime('%Y-%m-%d') if post.post_datetime_ist else None,
                'post_time': post.post_datetime_ist.strftime('%H:%M') if post.post_datetime_ist else None,
                'post_time_ago': post_time_ago,
                'post_day_of_week': post.post_datetime_ist.strftime('%A') if post.post_datetime_ist else None,
                
                # Engagement
                'like_count': total_likes,
                'comment_count': total_comments,
                'save_count': total_saves,
                'share_count': total_shares,
                'video_view_count': post.video_view_count or 0,
                'total_engagement': total_engagement,
                'engagement_rate': round(engagement_rate, 2),
                
                # Formatted counts
                'like_count_formatted': _format_count(total_likes),
                'comment_count_formatted': _format_count(total_comments),
                'save_count_formatted': _format_count(total_saves),
                'share_count_formatted': _format_count(total_shares),
                'total_engagement_formatted': _format_count(total_engagement),
                
                # Location
                'location_name': post.location_name,
                'location_id': post.location_id,
                'has_location': bool(post.location_name),
                
                # Flags
                'is_ad': post.is_ad or False,
                'is_sponsored': post.is_sponsored or False,
                
                # Metadata
                'first_fetched': post.first_fetched.isoformat() if post.first_fetched else None,
                'last_updated': post.last_updated.isoformat() if post.last_updated else None
            }
            posts_data.append(post_data)
        
        # Summary statistics
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

@profiles_bp.route('/comments/<media_id>', methods=['GET'])
def get_media_comments(media_id):
    """Get comments for a specific media post"""
    try:
        # For now, return empty comments since we'll add this functionality later
        return jsonify({
            'success': True,
            'data': [],
            'message': 'Comments functionality coming soon',
            'media_id': media_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
