"""
API Routes for Instagram Analytics
"""
from flask import Blueprint, request, jsonify, Response
from services.instagram_service import InstagramAnalyticsService
from services.chatbot_service import analytics_chatbot
from services.analytics_service import AnalyticsService
from services.calculation_methods_extractor import calculation_extractor
from models.database import db, Profile, MediaPost, Story, DailyMetrics
from sqlalchemy import func, desc
import os
import requests
import uuid
import asyncio
from datetime import datetime, timedelta
import base64

api_bp = Blueprint('api', __name__)

# Initialize the services
instagram_service = InstagramAnalyticsService(os.getenv('API_KEY'))
analytics_service = AnalyticsService()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@api_bp.route('/proxy/image', methods=['GET'])
def proxy_image():
    """Proxy Instagram images to bypass CORS restrictions"""
    try:
        image_url = request.args.get('url')
        if not image_url:
            return jsonify({'error': 'URL parameter is required'}), 400
        
        # Validate that it's an Instagram URL for security
        if not ('instagram.com' in image_url or 'cdninstagram.com' in image_url):
            return jsonify({'error': 'Only Instagram URLs are allowed'}), 400
        
        # Fetch the image from Instagram
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(image_url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        
        # Return the image with appropriate headers
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            generate(),
            headers={
                'Content-Type': response.headers.get('Content-Type', 'image/jpeg'),
                'Content-Length': response.headers.get('Content-Length', ''),
                'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch image: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

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
    """Get performance insights using centralized analytics service"""
    try:
        username = request.args.get('username')
        days = int(request.args.get('days', 30))
        
        # Use centralized analytics service instead of instagram_service
        insights = analytics_service.get_performance_insights(username, days)
        
        return jsonify({
            'success': True,
            'data': insights
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analytics/daily-chart', methods=['GET'])
def get_daily_chart_data():
    """Get daily chart data for time series visualization using centralized analytics service"""
    try:
        username = request.args.get('username')
        days = int(request.args.get('days', 30))
        
        # Use centralized analytics service for daily chart data
        daily_data = analytics_service.get_daily_chart_data(username, days)
        
        return jsonify({
            'success': True,
            'data': daily_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analytics/comprehensive', methods=['GET'])
def get_comprehensive_analytics():
    """Get comprehensive analytics data including all metrics"""
    try:
        username = request.args.get('username')
        days = int(request.args.get('days', 30))
        include_sections = request.args.get('sections', '').split(',') if request.args.get('sections') else None
        
        # Use centralized analytics service for comprehensive data
        analytics = analytics_service.get_comprehensive_analytics(username, days, include_sections)
        
        return jsonify({
            'success': True,
            'data': analytics
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analytics/weekly-comparison', methods=['GET'])
def get_weekly_comparison():
    """Get period-over-period comparison using centralized analytics service"""
    try:
        username = request.args.get('username')
        period = request.args.get('period', 'week')  # Default to week
        start_date = request.args.get('start_date')  # For custom period
        end_date = request.args.get('end_date')  # For custom period
        
        # Use centralized analytics service instead of instagram_service
        comparison = analytics_service.get_weekly_comparison(username, period, start_date, end_date)
        
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

@api_bp.route('/dashboard/<username>', methods=['GET'])
def get_dashboard_data(username):
    """Get dashboard data for specific username using centralized analytics service"""
    try:
        days = int(request.args.get('days', 30))
        
        # Use centralized analytics service
        analytics = analytics_service.get_comprehensive_analytics(
            username=username, 
            days=days,
            include_sections=['profiles', 'posts', 'hashtags', 'media_types', 'posting_times', 'performance']
        )
        
        # Get profile data
        profile_data = analytics['profiles']['profiles_data']
        current_profile = next((p for p in profile_data if p['username'] == username), {})
        
        # Extract and format dashboard data
        posts_data = analytics['posts']['posts_data']
        basic_stats = analytics['posts']['basic_stats']
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_posts = [p for p in posts_data if p['posted_at'] and 
                       datetime.fromisoformat(p['posted_at'].replace('Z', '+00:00')).replace(tzinfo=None) >= week_ago]
        
        # Top performing post
        top_post = None
        if posts_data:
            top_post_data = max(posts_data, key=lambda x: x['engagement'])
            top_post = {
                'id': top_post_data.get('link', ''),
                'username': top_post_data['username'],
                'og_username': top_post_data['username'],
                'media_type': top_post_data['media_type'],
                'like_count': top_post_data['likes'],
                'comment_count': top_post_data['comments'],
                'post_datetime_ist': top_post_data['posted_at'],
                'engagement': top_post_data['engagement']
            }
        
        # Calculate correct engagement rate
        followers = current_profile.get('followers', 1)
        avg_engagement = basic_stats.get('avg_engagement_per_post', 0)
        engagement_rate = round((avg_engagement / followers) * 100, 2) if followers > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_profiles': 1,
                'total_posts': basic_stats.get('total_posts', 0),
                'active_stories': analytics['stories']['total_active_stories'],
                'recent_posts_week': len(recent_posts),
                'top_post_week': top_post,
                'total_engagement': basic_stats.get('total_engagement', 0),
                'avg_engagement': avg_engagement,
                'engagement_rate': engagement_rate,
                'followers': followers,
                'following': current_profile.get('following', 0),
                'profile': current_profile
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/stats/summary', methods=['GET'])
def get_summary_stats():
    """Get summary statistics using centralized analytics service"""
    try:
        username = request.args.get('username')
        days = int(request.args.get('days', 30))
        
        # Use centralized analytics service
        analytics = analytics_service.get_comprehensive_analytics(
            username=username, 
            days=days,
            include_sections=['profiles', 'posts', 'stories', 'performance']
        )
        
        # Extract summary data
        posts_data = analytics['posts']['posts_data']
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_posts = [p for p in posts_data if p['posted_at'] and 
                       datetime.fromisoformat(p['posted_at'].replace('Z', '+00:00')).replace(tzinfo=None) >= week_ago]
        
        # Top performing post
        top_post = None
        if posts_data:
            top_post_data = max(posts_data, key=lambda x: x['engagement'])
            top_post = {
                'id': top_post_data.get('link', ''),
                'username': top_post_data['username'],
                'og_username': top_post_data['username'],
                'media_type': top_post_data['media_type'],
                'like_count': top_post_data['likes'],
                'comment_count': top_post_data['comments'],
                'post_datetime_ist': top_post_data['posted_at'],
                'engagement': top_post_data['engagement']
            }
        
        return jsonify({
            'success': True,
            'data': {
                'total_profiles': analytics['metadata']['total_profiles'],
                'total_posts': analytics['metadata']['total_posts'],
                'active_stories': analytics['stories']['total_active_stories'],
                'recent_posts_week': len(recent_posts),
                'top_post_week': top_post,
                'total_engagement': analytics['metadata']['total_engagement'],
                'avg_engagement': analytics['posts']['basic_stats']['avg_engagement_per_post']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Chatbot endpoints
@api_bp.route('/chatbot/chat', methods=['POST'])
def chatbot_chat():
    """Send a message to the analytics chatbot"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        username = data.get('username')  # Optional filter for specific account
        days = int(data.get('days', 30))  # Time period for analytics
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Since we can't use async in Flask directly, we'll call the sync version
        response = analytics_chatbot.chat_sync(message, session_id, username, days)
        
        return jsonify({
            'success': True,
            'data': response
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/chatbot/history/<session_id>', methods=['GET'])
def get_chatbot_history(session_id):
    """Get conversation history for a session"""
    try:
        history = analytics_chatbot.get_conversation_history(session_id)
        summary = analytics_chatbot.get_conversation_summary(session_id)
        
        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'summary': summary
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/chatbot/clear/<session_id>', methods=['DELETE'])
def clear_chatbot_history(session_id):
    """Clear conversation history for a session"""
    try:
        analytics_chatbot.clear_conversation(session_id)
        
        return jsonify({
            'success': True,
            'message': 'Conversation history cleared'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/chatbot/analytics-context', methods=['GET'])
def get_analytics_context():
    """Get current analytics context that the chatbot uses"""
    try:
        username = request.args.get('username')
        days = int(request.args.get('days', 30))
        
        context = analytics_chatbot.get_analytics_context(username, days)
        
        return jsonify({
            'success': True,
            'data': context
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analytics/calculation-methods', methods=['GET'])
def get_calculation_methods():
    """Get all calculation methods and formulas for transparency"""
    try:
        documentation = calculation_extractor.get_analytics_documentation()
        
        return jsonify({
            'success': True,
            'data': documentation.get('data', {}),
            'metadata': documentation.get('metadata', {})
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e),
            'data': {}
        }), 500

# Content Creation Endpoints
@api_bp.route('/content/create', methods=['POST'])
def create_content():
    """Create content using AI/LLM services"""
    try:
        from content_creation import create_content_endpoint
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(create_content_endpoint(data))
        finally:
            loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'content_id': '',
            'content_type': data.get('content_type', 'unknown') if 'data' in locals() else 'unknown',
            'error': str(e),
            'debug_info': {'endpoint_error': str(e)}
        }), 500

@api_bp.route('/content/conversation/<session_id>', methods=['GET'])
def get_conversation_history(session_id):
    """Get conversation history for a session"""
    try:
        from content_creation import get_conversation_history_endpoint
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(get_conversation_history_endpoint(session_id))
        finally:
            loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'history': []
        }), 500

@api_bp.route('/content/analytics-context/<username>', methods=['GET'])
def get_analytics_context_for_content(username):
    """Get analytics context for content creation"""
    try:
        # Get comprehensive analytics for the user
        analytics_data = analytics_service.get_comprehensive_analytics(username)
        
        # Also get performance insights for additional context
        insights = analytics_service.get_performance_insights(username, days=30)
        
        # Combine the data for content creation context
        context = {
            'username': username,
            'analytics': analytics_data,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'context': context
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'context': {}
        }), 500
