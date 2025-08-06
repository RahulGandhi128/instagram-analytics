"""
API Routes for Instagram Analytics
"""
from flask import Blueprint, request, jsonify
from services.instagram_service import InstagramAnalyticsService
from models.database import db, Profile, MediaPost, Story, DailyMetrics
from sqlalchemy import func, desc
import os
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)

# Initialize the service
instagram_service = InstagramAnalyticsService(os.getenv('API_KEY'))

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@api_bp.route('/profiles', methods=['POST'])
def add_profile():
    """Add a new profile username"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'success': False, 'error': 'Username is required'}), 400
        
        # Check if profile already exists
        existing_profile = Profile.query.get(username)
        if existing_profile:
            return jsonify({'success': False, 'error': 'Profile already exists'}), 400
        
        # Fetch data for the new username
        result = instagram_service.fetch_data_for_username(username)
        
        if result:
            return jsonify({
                'success': True,
                'message': f'Profile {username} added and data fetched successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to fetch data for username {username}. Please check if the username exists on Instagram.'
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/profiles/<username>', methods=['DELETE'])
def delete_profile(username):
    """Delete a profile and all associated data"""
    try:
        # Check if profile exists
        profile = Profile.query.get(username)
        if not profile:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404
        
        # Delete associated media posts
        MediaPost.query.filter(MediaPost.og_username == username).delete()
        
        # Delete associated stories
        Story.query.filter(Story.og_username == username).delete()
        
        # Delete associated daily metrics
        DailyMetrics.query.filter(DailyMetrics.username == username).delete()
        
        # Delete the profile
        db.session.delete(profile)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Profile {username} and all associated data deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/profiles', methods=['GET'])
def get_profiles():
    """Get all profiles with engagement rates"""
    try:
        profiles = Profile.query.all()
        profile_data = []
        
        for profile in profiles:
            profile_dict = profile.to_dict()
            
            # Calculate engagement rate for recent posts (last 30 days)
            engagement_rate = calculate_engagement_rate(profile.username)
            profile_dict['engagement_rate'] = engagement_rate
            
            profile_data.append(profile_dict)
        
        return jsonify({
            'success': True,
            'data': profile_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def calculate_engagement_rate(username):
    """Calculate engagement rate for a profile based on recent posts"""
    try:
        # Get profile to get follower count
        profile = Profile.query.get(username)
        if not profile or profile.follower_count == 0:
            return 0.0
        
        # Get recent posts (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_posts = MediaPost.query.filter(
            MediaPost.og_username == username,
            MediaPost.post_datetime_ist >= thirty_days_ago
        ).all()
        
        if not recent_posts:
            return 0.0
        
        # Calculate total engagement (likes + comments + shares + saves)
        total_engagement = 0
        for post in recent_posts:
            post_engagement = (post.like_count or 0) + (post.comment_count or 0) + (post.reshare_count or 0)
            # Note: Instagram API doesn't provide saves count, so we use available metrics
            total_engagement += post_engagement
        
        # Calculate average engagement per post
        avg_engagement_per_post = total_engagement / len(recent_posts)
        
        # Calculate engagement rate as percentage
        # Formula: (Average Engagement per Post / Followers) * 100
        engagement_rate = (avg_engagement_per_post / profile.follower_count) * 100
        
        return round(engagement_rate, 2)
        
    except Exception as e:
        print(f"Error calculating engagement rate for {username}: {e}")
        return 0.0

@api_bp.route('/fetch-data', methods=['POST'])
def fetch_data():
    """Trigger data fetching for all usernames"""
    try:
        instagram_service.fetch_all_data()
        return jsonify({
            'success': True,
            'message': 'Data fetching completed for all usernames'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/fetch-instagram-data', methods=['POST'])
def fetch_instagram_data():
    """Trigger data fetching for all usernames (legacy route)"""
    try:
        instagram_service.fetch_all_data()
        return jsonify({
            'success': True,
            'message': 'Data fetching completed for all usernames'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/fetch-instagram-data/<username>', methods=['POST'])
def fetch_instagram_data_username(username):
    """Trigger data fetching for specific username"""
    try:
        result = instagram_service.fetch_data_for_username(username)
        if result:
            return jsonify({
                'success': True,
                'message': f'Data fetching completed for {username}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to fetch data for {username}'
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/profiles/<username>', methods=['GET'])
def get_profile(username):
    """Get specific profile"""
    try:
        profile = Profile.query.get(username)
        if not profile:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404
        
        return jsonify({
            'success': True,
            'data': profile.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/media', methods=['GET'])
def get_media():
    """Get media posts with optional filtering"""
    try:
        username = request.args.get('username')
        limit = int(request.args.get('limit', 50))
        media_type = request.args.get('media_type')
        
        query = MediaPost.query
        
        if username:
            query = query.filter(MediaPost.og_username == username)
        
        if media_type:
            query = query.filter(MediaPost.media_type == media_type)
        
        media_posts = query.order_by(desc(MediaPost.post_datetime_ist)).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [post.to_dict() for post in media_posts],
            'total': len(media_posts)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/stories', methods=['GET'])
def get_stories():
    """Get current stories"""
    try:
        username = request.args.get('username')
        
        query = Story.query.filter(Story.expire_datetime_ist > datetime.now())
        
        if username:
            query = query.filter(Story.og_username == username)
        
        stories = query.order_by(desc(Story.post_datetime_ist)).all()
        
        return jsonify({
            'success': True,
            'data': [story.to_dict() for story in stories],
            'total': len(stories)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analytics/insights', methods=['GET'])
def get_insights():
    """Get performance insights"""
    try:
        username = request.args.get('username')
        days = int(request.args.get('days', 30))
        
        insights = instagram_service.get_performance_insights(username, days)
        
        return jsonify({
            'success': True,
            'data': insights
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analytics/weekly-comparison', methods=['GET'])
def get_weekly_comparison():
    """Get period-over-period comparison"""
    try:
        username = request.args.get('username')
        period = request.args.get('period', 'week')  # Default to week
        
        comparison = instagram_service.get_weekly_comparison(username, period)
        
        return jsonify({
            'success': True,
            'data': comparison
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analytics/daily-metrics', methods=['GET'])
def get_daily_metrics():
    """Get daily metrics for charts"""
    try:
        username = request.args.get('username')
        days = int(request.args.get('days', 30))
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        query = DailyMetrics.query.filter(
            DailyMetrics.date.between(start_date, end_date)
        ).order_by(DailyMetrics.date)
        
        if username:
            query = query.filter(DailyMetrics.username == username)
        
        metrics = query.all()
        
        return jsonify({
            'success': True,
            'data': [metric.to_dict() for metric in metrics]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/export/csv', methods=['GET'])
def export_csv():
    """Export data to CSV"""
    try:
        data_type = request.args.get('type', 'media')  # media, profiles, stories
        username = request.args.get('username')
        
        if data_type == 'profiles':
            query = Profile.query
            if username:
                query = query.filter(Profile.username == username)
            data = query.all()
            columns = ['username', 'full_name', 'follower_count', 'following_count', 'media_count', 'is_verified']
            
        elif data_type == 'stories':
            query = Story.query
            if username:
                query = query.filter(Story.og_username == username)
            data = query.all()
            columns = ['story_id', 'username', 'og_username', 'media_type', 'post_datetime_ist', 'expire_datetime_ist']
            
        else:  # media
            query = MediaPost.query
            if username:
                query = query.filter(MediaPost.og_username == username)
            data = query.all()
            columns = ['id', 'username', 'og_username', 'media_type', 'like_count', 'comment_count', 'post_datetime_ist', 'link']
        
        # Convert to dict format
        csv_data = []
        for item in data:
            item_dict = item.to_dict()
            filtered_dict = {col: item_dict.get(col, '') for col in columns}
            csv_data.append(filtered_dict)
        
        return jsonify({
            'success': True,
            'data': csv_data,
            'filename': f'{data_type}_{username or "all"}_{datetime.now().strftime("%Y%m%d")}.csv'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/stats/summary', methods=['GET'])
def get_summary_stats():
    """Get summary statistics"""
    try:
        total_profiles = Profile.query.count()
        total_posts = MediaPost.query.count()
        total_stories = Story.query.filter(Story.expire_datetime_ist > datetime.now()).count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_posts = MediaPost.query.filter(MediaPost.first_fetched > week_ago).count()
        
        # Top performing post this week
        top_post = MediaPost.query.filter(
            MediaPost.post_datetime_ist > week_ago
        ).order_by(desc(MediaPost.like_count + MediaPost.comment_count)).first()
        
        return jsonify({
            'success': True,
            'data': {
                'total_profiles': total_profiles,
                'total_posts': total_posts,
                'active_stories': total_stories,
                'recent_posts_week': recent_posts,
                'top_post_week': top_post.to_dict() if top_post else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
