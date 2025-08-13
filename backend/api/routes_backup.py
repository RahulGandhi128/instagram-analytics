"""
API Routes for Instagram Analytics
"""
from flask import Blueprint, request, jsonify, Response
from services.instagram_service import InstagramAnalyticsService
from services.star_api_service import create_star_api_service
from services.chatbot_service import analytics_chatbot
from services.analytics_service import AnalyticsService
from services.calculation_methods_extractor import calculation_extractor
from services.brainstormer_service import brainstormer_service
from models.database import db, Profile, MediaPost, Story, DailyMetrics, Highlight, FollowerData, MediaComment, HashtagData
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

@api_bp.route('/download/image', methods=['GET'])
def download_image():
    """Download generated images (DALL-E) by proxying through server to avoid CORS"""
    try:
        image_url = request.args.get('url')
        filename = request.args.get('filename', 'generated-image.png')
        
        if not image_url:
            return jsonify({'error': 'URL parameter is required'}), 400
        
        # Validate that it's an OpenAI DALL-E URL for security
        if not ('oaidalleapiprodscus.blob.core.windows.net' in image_url or 'openai.com' in image_url):
            return jsonify({'error': 'Only OpenAI DALL-E URLs are allowed'}), 400
        
        # Fetch the image from OpenAI
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(image_url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Return the image as download with appropriate headers
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            generate(),
            headers={
                'Content-Type': response.headers.get('Content-Type', 'image/png'),
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': response.headers.get('Content-Length', ''),
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to download image: {str(e)}'}), 500
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
            days=days
        )
        
        # Extract summary data from analytics
        posts_data = analytics.get('posts', {}).get('data', [])
        stories_data = analytics.get('stories', {}).get('data', [])
        
        # Calculate recent activity (last week)
        week_ago = datetime.now() - timedelta(days=7)
        recent_posts = [p for p in posts_data if p.get('posted_at') and 
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
                'average_engagement': analytics['metadata']['average_engagement'],
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analytics/summary-stats', methods=['GET'])
def get_analytics_summary_stats():
    """Get summary statistics for analytics dashboard"""
    try:
        # Get basic database counts
        stats = {
            'total_profiles': Profile.query.count(),
            'total_media_posts': MediaPost.query.count(),
            'total_stories': Story.query.count(),
            'total_daily_metrics': DailyMetrics.query.count(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        # Get basic database counts
        stats = {
            'total_profiles': Profile.query.count(),
            'total_media_posts': MediaPost.query.count(),
            'total_stories': Story.query.count(),
            'total_daily_metrics': DailyMetrics.query.count(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/analytics/daily-trends', methods=['GET'])
def get_daily_trends():
    """Get daily trends data"""
    try:
        username = request.args.get('username')
        days = int(request.args.get('days', 30))
        
        # Use centralized analytics service
        analytics = analytics_service.get_daily_chart_data(username, days)
        
        return jsonify({
            'success': True,
            'data': analytics
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
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


@api_bp.route('/brainstormer/chat', methods=['POST'])
def brainstormer_chat():
    """Generate brainstorming response based on analytics data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        message = data.get('message', '').strip()
        session_id = data.get('session_id', '')
        analytics_data = data.get('analytics_data', {})
        username = data.get('username')
        time_range = data.get('time_range', 30)
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        # Generate brainstorm response
        response_data = brainstormer_service.generate_brainstorm_response(
            user_message=message,
            session_id=session_id,
            analytics_data=analytics_data,
            username=username,
            time_range=time_range
        )
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to generate brainstorm response: {str(e)}',
            'response': 'I apologize, but I encountered an error while processing your request. Please try again.',
            'suggestions': []
        }), 500

# Star API Enhanced Data Collection Endpoints
@api_bp.route('/star-api/collect-comprehensive/<username>', methods=['POST'])
def collect_comprehensive_data(username):
    """
    Collect comprehensive data for a user using Star API
    """
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        star_service = create_star_api_service(api_key)
        result = star_service.collect_comprehensive_data(username)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/star-api/test-endpoints', methods=['POST'])
def test_star_api_endpoints():
    """
    Test all Star API endpoints with a sample username
    """
    try:
        data = request.get_json()
        test_username = data.get('username', 'instagram')
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        star_service = create_star_api_service(api_key)
        test_results = star_service.test_all_endpoints(test_username)
        
        return jsonify({
            'success': True,
            'data': test_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/star-api/user-info/<username>', methods=['GET'])
def get_star_user_info(username):
    """
    Get user info using Star API
    """
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        star_service = create_star_api_service(api_key)
        user_data = star_service.get_user_info_by_username(username)
        
        if user_data:
            return jsonify({
                'success': True,
                'data': user_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch user data'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/star-api/user-media/<username>', methods=['GET'])
def get_star_user_media(username):
    """
    Get user media using Star API
    """
    try:
        count = request.args.get('count', 50, type=int)
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        star_service = create_star_api_service(api_key)
        
        # First get user info to extract user_id
        user_info = star_service.get_user_info_by_username(username)
        if not user_info:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Extract user_id with debug info
        try:
            # Debug: Print the structure to see what we have
            print(f"DEBUG MEDIA: user_info structure = {list(user_info.keys())}")
            if 'data' in user_info:
                print(f"DEBUG MEDIA: user_info['data'] structure = {list(user_info['data'].keys())}")
                if 'response' in user_info['data']:
                    print(f"DEBUG MEDIA: response structure = {list(user_info['data']['response'].keys())}")
            
            user_id = user_info['data']['response']['body']['data']['user']['id']
            print(f"DEBUG MEDIA: Successfully extracted user_id = {user_id}")
        except (KeyError, TypeError) as e:
            print(f"DEBUG MEDIA: Failed to extract user_id: {e}")
            return jsonify({
                'success': False,
                'error': f'Could not extract user ID: {e}'
            }), 500
        
        # Get media using user_id
        media_data = star_service.get_user_media(user_id, count)
        
        if media_data:
            return jsonify({
                'success': True,
                'data': media_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch media data'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/star-api/user-stories/<username>', methods=['GET'])
def get_star_user_stories(username):
    """
    Get user stories using Star API
    """
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        star_service = create_star_api_service(api_key)
        
        # First get user info to extract user_id
        user_info = star_service.get_user_info_by_username(username)
        if not user_info:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Extract user_id with debug info
        try:
            # Debug: Print the structure to see what we have
            print(f"DEBUG STORIES: user_info structure = {list(user_info.keys())}")
            if 'data' in user_info:
                print(f"DEBUG STORIES: user_info['data'] structure = {list(user_info['data'].keys())}")
                if 'response' in user_info['data']:
                    print(f"DEBUG STORIES: response structure = {list(user_info['data']['response'].keys())}")
            
            user_id = user_info['data']['response']['body']['data']['user']['id']
            print(f"DEBUG STORIES: Successfully extracted user_id = {user_id}")
        except (KeyError, TypeError) as e:
            print(f"DEBUG STORIES: Failed to extract user_id: {e}")
            return jsonify({
                'success': False,
                'error': f'Could not extract user ID: {e}'
            }), 500
        
        # Get stories using user_id
        stories_data = star_service.get_user_stories(user_id)
        
        if stories_data:
            return jsonify({
                'success': True,
                'data': stories_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch stories data'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/star-api/database-status', methods=['GET'])
def get_database_status():
    """
    Get current database status and data counts
    """
    try:
        status = {
            'profiles': Profile.query.count(),
            'media_posts': MediaPost.query.count(),
            'stories': Story.query.count(),
            'daily_metrics': DailyMetrics.query.count(),
            'last_updated': {
                'profiles': db.session.query(func.max(Profile.last_updated)).scalar(),
                'media_posts': db.session.query(func.max(MediaPost.last_updated)).scalar(),
                'stories': db.session.query(func.max(Story.first_fetched)).scalar()
            }
        }
        
        # Convert datetime objects to strings
        for key, value in status['last_updated'].items():
            if value:
                status['last_updated'][key] = value.isoformat()
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
