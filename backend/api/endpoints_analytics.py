"""
Analytics Endpoints - All analytics, insights, dashboard, and export functionality
"""
from flask import Blueprint, request, jsonify, Response
from services.analytics_service import AnalyticsService
from services.calculation_methods_extractor import calculation_extractor
from models.database import db, Profile, MediaPost, Story
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import os

analytics_bp = Blueprint('analytics', __name__)

# Initialize the service
analytics_service = AnalyticsService()

@analytics_bp.route('/analytics/insights', methods=['GET'])
def get_insights():
    """
    Get analytics insights for a specific profile
    """
    try:
        username = request.args.get('username')
        days = request.args.get('days', 30, type=int)
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username parameter is required'
            }), 400

        insights = analytics_service.get_performance_insights(username, days)
        return jsonify({
            'success': True,
            'data': insights
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/daily-chart', methods=['GET'])
def get_daily_chart():
    """
    Get daily chart data for analytics
    """
    try:
        username = request.args.get('username')
        days = request.args.get('days', 30, type=int)
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username parameter is required'
            }), 400

        chart_data = analytics_service.get_daily_chart_data(username, days)
        return jsonify({
            'success': True,
            'data': chart_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/comprehensive', methods=['GET'])
def get_comprehensive_analytics():
    """
    Get comprehensive analytics for a profile
    """
    try:
        username = request.args.get('username')
        days = request.args.get('days', 30, type=int)
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username parameter is required'
            }), 400

        analytics = analytics_service.get_comprehensive_analytics(username, days)
        return jsonify({
            'success': True,
            'data': analytics
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/weekly-comparison', methods=['GET'])
def get_weekly_comparison():
    """
    Get weekly comparison analytics
    """
    try:
        username = request.args.get('username')
        days = request.args.get('days', 30, type=int)
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username parameter is required'
            }), 400

        comparison = analytics_service.get_weekly_comparison(username)
        return jsonify({
            'success': True,
            'data': comparison
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/daily-metrics', methods=['GET'])
def get_daily_metrics():
    """
    Get daily metrics for a profile
    """
    try:
        username = request.args.get('username')
        days = request.args.get('days', 30, type=int)
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username parameter is required'
            }), 400

        # Get profile
        profile = Profile.query.filter_by(username=username).first()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404

        # Get daily metrics
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get media posts for the date range instead of DailyMetrics
        media_posts = MediaPost.query.filter_by(profile_id=profile.id)\
                                   .filter(MediaPost.post_datetime_ist >= start_date)\
                                   .filter(MediaPost.post_datetime_ist <= end_date)\
                                   .order_by(MediaPost.post_datetime_ist)\
                                   .all()
        
        # Convert media posts to metrics format
        metrics = []
        for post in media_posts:
            metrics.append({
                'date': post.post_datetime_ist.date(),
                'likes': post.like_count or 0,
                'comments': post.comment_count or 0,
                'engagement': (post.like_count or 0) + (post.comment_count or 0)
            })

        return jsonify({
            'success': True,
            'data': [{
                'date': metric.date.isoformat(),
                'follower_count': metric.follower_count,
                'following_count': metric.following_count,
                'media_count': metric.media_count,
                'engagement_rate': metric.engagement_rate
            } for metric in metrics]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/export/csv', methods=['GET'])
def export_csv():
    """
    Export analytics data as CSV
    """
    try:
        return jsonify({
            'success': False,
            'error': 'CSV export feature is temporarily unavailable'
        }), 501

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/dashboard/<username>', methods=['GET'])
def get_dashboard_data(username):
    """
    Get comprehensive dashboard data for a profile
    """
    try:
        # Get profile
        profile = Profile.query.filter_by(username=username).first()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404

        # Get basic stats
        media_count = MediaPost.query.filter_by(profile_id=profile.id).count()
        story_count = Story.query.filter_by(profile_id=profile.id).count()
        
        # Get recent media
        recent_media = MediaPost.query.filter_by(profile_id=profile.id)\
                                    .order_by(desc(MediaPost.created_at))\
                                    .limit(6).all()
        
        # Get engagement stats
        total_likes = db.session.query(func.sum(MediaPost.like_count))\
                               .filter_by(profile_id=profile.id).scalar() or 0
        total_comments = db.session.query(func.sum(MediaPost.comment_count))\
                                  .filter_by(profile_id=profile.id).scalar() or 0
        
        # Calculate engagement rate
        engagement_rate = 0
        if profile.follower_count and profile.follower_count > 0:
            total_engagement = total_likes + total_comments
            engagement_rate = (total_engagement / (media_count * profile.follower_count)) * 100 if media_count > 0 else 0

        # Get recent stories
        recent_stories = Story.query.filter_by(profile_id=profile.id)\
                                  .order_by(desc(Story.created_at))\
                                  .limit(5).all()

        dashboard_data = {
            'profile': {
                'username': profile.username,
                'bio': profile.bio,
                'follower_count': profile.follower_count,
                'following_count': profile.following_count,
                'profile_pic_url': profile.profile_pic_url
            },
            'stats': {
                'media_count': media_count,
                'story_count': story_count,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'engagement_rate': round(engagement_rate, 2)
            },
            'recent_media': [{
                'id': media.id,
                'shortcode': media.shortcode,
                'display_url': media.display_url,
                'like_count': media.like_count,
                'comment_count': media.comment_count,
                'caption': media.caption[:100] if media.caption else '',
                'created_at': media.created_at.isoformat() if media.created_at else None
            } for media in recent_media],
            'recent_stories': [{
                'id': story.id,
                'story_id': story.story_id,
                'display_url': story.display_url,
                'story_type': story.story_type,
                'created_at': story.created_at.isoformat() if story.created_at else None
            } for story in recent_stories]
        }

        return jsonify({
            'success': True,
            'data': dashboard_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/stats/summary', methods=['GET'])
def get_stats_summary():
    """
    Get summary statistics across all profiles
    """
    try:
        username = request.args.get('username')
        
        if username:
            # Get stats for specific user
            profile = Profile.query.filter_by(username=username).first()
            if not profile:
                return jsonify({
                    'success': False,
                    'error': 'Profile not found'
                }), 404
            
            media_count = MediaPost.query.filter_by(profile_id=profile.id).count()
            story_count = Story.query.filter_by(profile_id=profile.id).count()
            total_likes = db.session.query(func.sum(MediaPost.like_count))\
                                   .filter_by(profile_id=profile.id).scalar() or 0
            total_comments = db.session.query(func.sum(MediaPost.comment_count))\
                                      .filter_by(profile_id=profile.id).scalar() or 0
            
            summary = {
                'profiles': 1,
                'total_media': media_count,
                'total_stories': story_count,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'avg_engagement': round((total_likes + total_comments) / max(media_count, 1), 2)
            }
        else:
            # Get global stats
            total_profiles = Profile.query.count()
            total_media = MediaPost.query.count()
            total_stories = Story.query.count()
            total_likes = db.session.query(func.sum(MediaPost.like_count)).scalar() or 0
            total_comments = db.session.query(func.sum(MediaPost.comment_count)).scalar() or 0
            
            summary = {
                'profiles': total_profiles,
                'total_media': total_media,
                'total_stories': total_stories,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'avg_engagement': round((total_likes + total_comments) / max(total_media, 1), 2)
            }

        return jsonify({
            'success': True,
            'data': summary
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/summary-stats', methods=['GET'])
def get_summary_stats():
    """
    Get summary analytics statistics
    """
    try:
        # Get total counts
        total_profiles = Profile.query.count()
        total_media = MediaPost.query.count()
        total_stories = Story.query.count()
        
        # Get engagement stats
        total_likes = db.session.query(func.sum(MediaPost.like_count)).scalar() or 0
        total_comments = db.session.query(func.sum(MediaPost.comment_count)).scalar() or 0
        
        # Calculate averages
        avg_likes_per_post = round(total_likes / max(total_media, 1), 2)
        avg_comments_per_post = round(total_comments / max(total_media, 1), 2)
        
        # Get top performing posts
        top_posts = MediaPost.query.order_by(desc(MediaPost.like_count)).limit(5).all()
        
        summary_stats = {
            'overview': {
                'total_profiles': total_profiles,
                'total_media': total_media,
                'total_stories': total_stories,
                'total_likes': total_likes,
                'total_comments': total_comments
            },
            'averages': {
                'avg_likes_per_post': avg_likes_per_post,
                'avg_comments_per_post': avg_comments_per_post,
                'total_engagement': total_likes + total_comments
            },
            'top_posts': [{
                'shortcode': post.shortcode,
                'like_count': post.like_count,
                'comment_count': post.comment_count,
                'display_url': post.display_url,
                'caption': post.caption[:100] if post.caption else ''
            } for post in top_posts]
        }

        return jsonify({
            'success': True,
            'data': summary_stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/daily-trends', methods=['GET'])
def get_daily_trends():
    """
    Get daily trends analysis
    """
    try:
        return jsonify({
            'success': False,
            'error': 'Daily trends feature is temporarily unavailable'
        }), 501

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/calculation-methods', methods=['GET'])
def get_calculation_methods():
    """
    Get detailed calculation methods for analytics
    """
    try:
        methods = {
            "engagement_rate": {
                "description": "Percentage of followers who engage with content",
                "formula": "(Likes + Comments) / Followers * 100",
                "interpretation": "Higher percentages indicate better audience engagement"
            },
            "avg_engagement": {
                "description": "Average engagement per post",
                "formula": "Total Engagement / Number of Posts",
                "interpretation": "Shows consistency of engagement across content"
            },
            "growth_rate": {
                "description": "Follower growth over time period",
                "formula": "(Current Followers - Previous Followers) / Previous Followers * 100",
                "interpretation": "Positive values indicate follower growth"
            },
            "best_posting_time": {
                "description": "Optimal time to post based on engagement patterns",
                "formula": "Time slots with highest average engagement",
                "interpretation": "Times when audience is most active"
            },
            "content_performance": {
                "description": "How different content types perform",
                "formula": "Average engagement per content type",
                "interpretation": "Identifies which content resonates most with audience"
            }
        }
        
        return jsonify({
            'success': True,
            'data': methods
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
