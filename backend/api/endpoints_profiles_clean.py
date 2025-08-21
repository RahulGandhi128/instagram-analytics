"""
Clean Instagram Analytics API Endpoints
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, func
from models.database import db, Profile, MediaPost
from datetime import datetime
import pytz
from models.database import MediaComment

# Define IST timezone
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
            media_count = MediaPost.query.filter_by(profile_id=profile.id).count()
            
            # Get latest media for engagement rate calculation
            latest_media = MediaPost.query.filter_by(profile_id=profile.id)\
                .order_by(desc(MediaPost.taken_at_timestamp)).limit(10).all()
            
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
        query = MediaPost.query.filter_by(profile_id=profile.id)
        
        # Filter by media type
        if media_type:
            query = query.filter_by(media_type=media_type)
        
        # Apply sorting
        if sort_by == 'engagement':
            engagement_expr = (
                func.coalesce(MediaPost.like_count, 0) +
                func.coalesce(MediaPost.comment_count, 0)
                # Note: save_count and share_count don't exist in current schema
            )
            query = query.order_by(desc(engagement_expr))
        elif sort_by == 'likes':
            query = query.order_by(desc(MediaPost.like_count))
        else:
            query = query.order_by(desc(MediaPost.taken_at_timestamp))
        
        # Get results
        media_posts = query.limit(limit).all()
        
        # Format data
        posts_data = []
        for post in media_posts:
            # Calculate metrics
            total_likes = post.like_count or 0
            total_comments = post.comment_count or 0
            total_saves = getattr(post, 'save_count', 0) or 0  # This field might not exist
            total_shares = getattr(post, 'share_count', 0) or 0  # This field might not exist
            total_engagement = total_likes + total_comments + total_saves + total_shares
            
            # Calculate engagement rate
            engagement_rate = 0
            if profile.followers_count and profile.followers_count > 0:
                engagement_rate = (total_engagement / profile.followers_count) * 100
            
            # Format time
            post_time_ago = ""
            if post.taken_at_timestamp:
                try:
                    # Use UTC for calculation since taken_at_timestamp is in UTC
                    time_diff = datetime.utcnow() - post.taken_at_timestamp
                    if time_diff.days > 0:
                        post_time_ago = f"{time_diff.days}d ago"
                    elif time_diff.seconds > 3600:
                        post_time_ago = f"{time_diff.seconds // 3600}h ago"
                    else:
                        post_time_ago = f"{time_diff.seconds // 60}m ago"
                except Exception as e:
                    post_time_ago = "Unknown"
            
            # Media icon
            media_icon = "📷"
            if post.is_video:
                media_icon = "🎥"
            elif post.media_type == 'reel':
                media_icon = "🎬"
            elif post.media_type == 'carousel':
                media_icon = "🖼️"
            
            post_data = {
                'id': post.id,
                'username': profile.username,  # Get username from profile, not post
                'shortcode': post.shortcode,
                'instagram_url': f"https://instagram.com/p/{post.shortcode}/" if post.shortcode else getattr(post, 'link', ''),
                'media_type': post.media_type or 'post',
                'media_icon': media_icon,
                'is_video': post.is_video or False,
                'carousel_media_count': 1 if post.media_type != 'carousel' else getattr(post, 'carousel_media_count', 1),
                'is_carousel': post.media_type == 'carousel',
                
                # Content
                'caption': post.caption,
                'caption_preview': post.caption[:100] + "..." if post.caption and len(post.caption) > 100 else post.caption,
                'display_url': post.display_url,
                'hashtags': getattr(post, 'hashtags', []) or [],
                'hashtags_count': len(getattr(post, 'hashtags', []) or []),
                'mentions': getattr(post, 'mentions', []) or [],
                'mentions_count': len(getattr(post, 'mentions', []) or []),
                
                # Timing
                'post_datetime_ist': post.taken_at_timestamp.isoformat() if post.taken_at_timestamp else None,
                'post_date': post.taken_at_timestamp.strftime('%Y-%m-%d') if post.taken_at_timestamp else None,
                'post_time': post.taken_at_timestamp.strftime('%H:%M') if post.taken_at_timestamp else None,
                'post_time_ago': post_time_ago,
                'post_day_of_week': post.taken_at_timestamp.strftime('%A') if post.taken_at_timestamp else None,
                
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
                'is_sponsored': getattr(post, 'is_sponsored', False) or False,
                
                # Metadata
                'first_fetched': getattr(post, 'first_fetched', None).isoformat() if getattr(post, 'first_fetched', None) else None,
                'last_updated': post.updated_at.isoformat() if post.updated_at else None
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
                'follower_count': profile.followers_count,
                'following_count': profile.following_count,
                'biography': profile.biography,
                'is_verified': profile.is_verified,
                'is_private': profile.is_private,
                'is_business_account': profile.is_business_account,
                'avg_engagement_rate': getattr(profile, 'avg_engagement_rate', 0) or 0
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

@profiles_bp.route('/profiles/<username>', methods=['DELETE'])
def delete_profile(username):
    """Delete a profile and all its associated data"""
    try:
        # Find the profile
        profile = Profile.query.filter_by(username=username).first()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        # Delete all associated data (cascade will handle this)
        db.session.delete(profile)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Profile {username} and all associated data deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/media/<shortcode>/comments', methods=['GET'])
def get_media_comments(shortcode):
    """Get comments for a specific media post"""
    try:
        # Find the media post by shortcode
        media_post = MediaPost.query.filter_by(shortcode=shortcode).first()
        if not media_post:
            return jsonify({'success': False, 'error': 'Media post not found'}), 404
        
        # Get comments for this post
        comments = MediaComment.query.filter_by(media_post_id=media_post.id).order_by(MediaComment.created_at.desc()).limit(25).all()
        
        comments_data = []
        for comment in comments:
            comment_data = {
                'id': comment.id,
                'instagram_id': comment.instagram_id,
                'text': comment.text,
                'created_at_utc': comment.created_at_utc.isoformat() if comment.created_at_utc else None,
                'like_count': comment.like_count,
                'owner_username': comment.owner_username,
                'owner_id': comment.owner_id,
                'owner_profile_pic_url': comment.owner_profile_pic_url,
                'owner_is_verified': comment.owner_is_verified,
                'parent_comment_id': comment.parent_comment_id,
                'reply_count': comment.reply_count
            }
            comments_data.append(comment_data)
        
        return jsonify({
            'success': True,
            'data': comments_data,
            'total_comments': len(comments_data),
            'media_post_id': media_post.id,
            'shortcode': shortcode
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
