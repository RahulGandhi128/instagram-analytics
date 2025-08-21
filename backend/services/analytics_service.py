"""
Centralized Analytics Service
Single source of truth for all Instagram analytics calculations
Eliminates redundancy across chatbot_service.py, instagram_service.py, and routes.py
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy import func, desc
from models.database import db, Profile, MediaPost, Story
from collections import defaultdict
from config.analytics_config import ANALYTICS_SECTIONS, PERFORMANCE_THRESHOLDS, DATA_LIMITS
import re


class AnalyticsService:
    def __init__(self):
        self.cache = {}  # Optional: Add caching for performance
        
    def get_comprehensive_analytics(self, 
                                  username: Optional[str] = None, 
                                  days: int = 30,
                                  include_sections: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Master method that calculates all analytics data
        
        Args:
            username: Filter by specific username
            days: Time period for analysis
            include_sections: List of sections to include (for performance)
                            ['profiles', 'posts', 'hashtags', 'media_types', 
                             'posting_times', 'engagement_trends', 'performance', 'stories']
        """
        if include_sections is None:
            include_sections = ANALYTICS_SECTIONS.get('full', [
                'profiles', 'posts', 'hashtags', 'media_types', 
                'posting_times', 'engagement_trends', 'performance', 'stories'
            ])
        
        # Ensure include_sections is not None for type checking
        sections = include_sections or []
        
        # Base data collection
        base_data = self._get_base_data(username, days)
        
        analytics = {
            'metadata': {
                'period_days': days,
                'username_filter': username,
                'generated_at': datetime.now().isoformat(),
                'total_profiles': len(base_data['profiles']),
                'total_posts': len(base_data['posts']),
                'total_engagement': base_data['total_engagement'],
                'included_sections': include_sections
            }
        }
        
        # Modular analytics calculation
        if 'profiles' in sections:
            analytics['profiles'] = self._calculate_profile_analytics(base_data)
            
        if 'posts' in sections:
            analytics['posts'] = self._calculate_post_analytics(base_data)
            
        if 'hashtags' in sections:
            analytics['hashtags'] = self._calculate_hashtag_analytics(base_data)
            
        if 'media_types' in sections:
            analytics['media_types'] = self._calculate_media_type_analytics(base_data)
            
        if 'posting_times' in sections:
            analytics['posting_times'] = self._calculate_optimal_posting_times(base_data)
            
        if 'engagement_trends' in sections:
            analytics['engagement_trends'] = self._calculate_engagement_trends(base_data, days)
            
        if 'performance' in sections:
            analytics['performance'] = self._calculate_performance_insights(base_data)
            
        if 'stories' in sections:
            analytics['stories'] = self._calculate_story_analytics(base_data)
        
        return analytics
    
    def _get_base_data(self, username: Optional[str], days: int) -> Dict[str, Any]:
        """Collect all base data in single database hit"""
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Base queries
        profiles_query = Profile.query
        posts_query = MediaPost.query.filter(MediaPost.taken_at_timestamp >= start_date)
        stories_query = Story.query.filter(Story.expiring_at_timestamp > datetime.now())
        
        # Apply username filter if specified
        if username:
            profiles_query = profiles_query.filter(Profile.username == username)
            posts_query = posts_query.join(Profile).filter(Profile.username == username)
            stories_query = stories_query.join(Profile).filter(Profile.username == username)
        
        # Execute queries
        profiles = profiles_query.all()
        posts = posts_query.all()
        stories = stories_query.all()
        
        # Calculate total engagement
        total_engagement = sum((post.like_count or 0) + (post.comment_count or 0) for post in posts)
        total_likes = sum(post.like_count or 0 for post in posts)
        total_comments = sum(post.comment_count or 0 for post in posts)
        
        return {
            'profiles': profiles,
            'posts': posts,
            'stories': stories,
            'total_engagement': total_engagement,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'start_date': start_date,
            'end_date': end_date
        }
    
    def _calculate_profile_analytics(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate profile-related analytics"""
        profiles = base_data['profiles']
        
        profile_data = []
        for profile in profiles:
            profile_data.append({
                'username': profile.username,
                'full_name': profile.full_name,
                'followers': profile.followers_count,
                'following': profile.following_count,
                'posts_count': profile.media_count,
                'is_verified': profile.is_verified,
                'is_private': getattr(profile, 'is_private', False),
                'bio': getattr(profile, 'bio', ''),
                'engagement_rate': getattr(profile, 'engagement_rate', 0)
            })
        
        return {
            'profiles_data': profile_data,
            'total_profiles': len(profiles),
            'verified_count': sum(1 for p in profiles if p.is_verified),
            'private_count': sum(1 for p in profiles if getattr(p, 'is_private', False)),
            'total_followers': sum(p.followers_count or 0 for p in profiles),
            'total_following': sum(p.following_count or 0 for p in profiles),
            'avg_followers': (sum(p.followers_count or 0 for p in profiles) / len(profiles)) if profiles else 0,
            'avg_following': (sum(p.following_count or 0 for p in profiles) / len(profiles)) if profiles else 0
        }
    
    def _calculate_post_analytics(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate post-related analytics"""
        posts = base_data['posts']
        total_engagement = base_data['total_engagement']
        total_likes = base_data['total_likes']
        total_comments = base_data['total_comments']
        
        # Content type breakdown
        content_types = {'post': 0, 'reel': 0, 'carousel': 0}
        content_engagement = {'post': 0, 'reel': 0, 'carousel': 0}
        collab_count = 0
        total_play_count = 0
        reel_count = 0
        total_reshares = 0
        
        for post in posts:
            media_type = post.media_type or 'post'
            post_engagement = (post.like_count or 0) + (post.comment_count or 0)
            
            # Count content types
            if media_type in content_types:
                content_types[media_type] += 1
                content_engagement[media_type] += post_engagement
            
            # Count collaborations
            if getattr(post, 'is_collab', False):
                collab_count += 1
            
            # Count reel views (for average reel view calculation)
            if media_type == 'reel' and getattr(post, 'play_count', 0):
                total_play_count += post.play_count
                reel_count += 1
            
            # Count reshares (part of total engagement)
            if getattr(post, 'reshare_count', 0):
                total_reshares += post.reshare_count
        
        # Basic stats
        total_content = sum(content_types.values())
        extended_engagement = total_engagement + total_reshares  # likes + comments + reshares
        
        basic_stats = {
            'total_posts': len(posts),
            'total_content': total_content,  # New: Total content count
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_engagement': total_engagement,  # likes + comments only
            'extended_engagement': extended_engagement,  # likes + comments + reshares
            'total_reshares': total_reshares,
            'avg_likes': total_likes / len(posts) if posts else 0,
            'avg_comments': total_comments / len(posts) if posts else 0,
            'avg_engagement_per_post': total_engagement / len(posts) if posts else 0,
            'engagement_per_content': extended_engagement / total_content if total_content > 0 else 0,  # New metric
            'average_reel_view': total_play_count / reel_count if reel_count > 0 else 0,  # New metric
            'collab_content_count': collab_count,  # New: Count of collaborations
            'content_type_breakdown': content_types,  # New: Breakdown by type
            'content_engagement_breakdown': content_engagement  # New: Engagement by type
        }
        
        # Detailed posts data
        posts_data = []
        for post in posts:
            post_engagement = (post.like_count or 0) + (post.comment_count or 0)
            posts_data.append({
                'username': post.profile.username if post.profile else 'unknown',
                'media_type': post.media_type,
                'likes': post.like_count or 0,
                'comments': post.comment_count or 0,
                'reshares': getattr(post, 'reshare_count', 0),
                'play_count': getattr(post, 'play_count', 0),
                'is_collab': getattr(post, 'is_collab', False),
                'engagement': post_engagement,
                'extended_engagement': post_engagement + (getattr(post, 'reshare_count', 0)),
                'posted_at': post.taken_at_timestamp.isoformat() if post.taken_at_timestamp else None,
                'caption': post.caption[:200] + '...' if post.caption and len(post.caption) > 200 else post.caption,
                'link': getattr(post, 'link', ''),
                'engagement_count': post_engagement  # For compatibility
            })
        
        # Top and bottom performing posts
        posts_by_engagement = sorted(posts_data, key=lambda x: x['extended_engagement'], reverse=True)
        top_posts = posts_by_engagement[:10]
        bottom_posts = posts_by_engagement[-5:] if len(posts_by_engagement) >= 5 else posts_by_engagement
        
        # Top performers (content where engagement > engagement per content)
        engagement_threshold = basic_stats['engagement_per_content']
        top_performers = [p for p in posts_data if p['extended_engagement'] > engagement_threshold]
        
        # Top post of the period
        top_post_engagement = max([p['extended_engagement'] for p in posts_data], default=0)
        
        return {
            'basic_stats': basic_stats,
            'posts_data': posts_data,
            'top_posts': top_posts,
            'bottom_posts': bottom_posts,
            'best_performing_posts': top_posts,
            'worst_performing_posts': bottom_posts,
            'top_performers': top_performers,  # New: Posts above average engagement
            'top_performers_count': len(top_performers),  # New: Count of top performers
            'top_post_engagement': top_post_engagement
        }
    
    def _calculate_hashtag_analytics(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive hashtag analytics"""
        posts = base_data['posts']
        
        hashtag_performance = {}
        
        # Extract hashtags from all posts
        for post in posts:
            if post.caption:
                hashtags = re.findall(r'#\w+', post.caption.lower())
                post_engagement = (post.like_count or 0) + (post.comment_count or 0)
                
                for hashtag in hashtags:
                    if hashtag not in hashtag_performance:
                        hashtag_performance[hashtag] = {'count': 0, 'total_engagement': 0}
                    hashtag_performance[hashtag]['count'] += 1
                    hashtag_performance[hashtag]['total_engagement'] += post_engagement
        
        # Calculate average engagement per hashtag use
        for hashtag in hashtag_performance:
            hashtag_performance[hashtag]['avg_engagement'] = (
                hashtag_performance[hashtag]['total_engagement'] / 
                hashtag_performance[hashtag]['count']
            )
        
        # Top hashtags by total engagement
        top_hashtags_total = sorted(
            hashtag_performance.items(),
            key=lambda x: x[1]['total_engagement'],
            reverse=True
        )[:15]
        
        # Top hashtags by average engagement (unique hashtags)
        top_hashtags_avg = sorted(
            hashtag_performance.items(),
            key=lambda x: x[1]['avg_engagement'],
            reverse=True
        )[:15]
        
        return {
            'hashtag_performance': hashtag_performance,
            'top_hashtags_by_total_engagement': [
                {
                    'hashtag': tag.replace('#', ''), 
                    'usage_count': data['count'], 
                    'total_posts': data['count'],  # For trending analysis compatibility
                    'total_engagement': data['total_engagement'],
                    'avg_engagement': data['avg_engagement']
                } 
                for tag, data in top_hashtags_total
            ],
            'top_hashtags_by_avg_engagement': [
                {
                    'hashtag': tag.replace('#', ''), 
                    'usage_count': data['count'], 
                    'total_posts': data['count'],  # For trending analysis compatibility
                    'total_engagement': data['total_engagement'],
                    'avg_engagement': data['avg_engagement']
                } 
                for tag, data in top_hashtags_avg
            ],
            'trending_hashtags': [  # New: Formatted for trending analysis
                {
                    'hashtag': f"#{tag.replace('#', '')}", 
                    'total_posts': data['count'], 
                    'total_engagement': data['total_engagement'],
                    'avg_engagement': data['avg_engagement'],
                    'engagement_display': f"{data['total_engagement']:,}" if data['total_engagement'] >= 1000 else str(data['total_engagement'])
                } 
                for tag, data in top_hashtags_total
            ],
            'total_unique_hashtags': len(hashtag_performance),
            'top_hashtags': [  # Legacy compatibility
                {
                    'hashtag': tag.replace('#', ''), 
                    'usage_count': data['count'], 
                    'total_engagement': data['total_engagement'],
                    'avg_engagement': data['avg_engagement']
                } 
                for tag, data in top_hashtags_total[:10]
            ]
        }
    
    def _calculate_media_type_analytics(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate media type performance analytics"""
        posts = base_data['posts']
        
        # Initialize with standard Instagram media types
        media_type_stats = {
            'post': {'count': 0, 'total_engagement': 0, 'avg_engagement': 0.0},
            'reel': {'count': 0, 'total_engagement': 0, 'avg_engagement': 0.0},
            'carousel': {'count': 0, 'total_engagement': 0, 'avg_engagement': 0.0}
        }
        
        for post in posts:
            # Normalize media type names
            media_type = post.media_type or 'post'
            if media_type.lower() == 'carousel_album':
                media_type = 'carousel'
            elif media_type.lower() == 'video':
                media_type = 'reel'
            elif media_type.lower() == 'image':
                media_type = 'post'
            
            # Ensure media type exists in our stats
            if media_type not in media_type_stats:
                media_type_stats[media_type] = {'count': 0, 'total_engagement': 0, 'avg_engagement': 0.0}
            
            post_engagement = (post.like_count or 0) + (post.comment_count or 0)
            
            media_type_stats[media_type]['count'] += 1
            media_type_stats[media_type]['total_engagement'] += post_engagement
        
        # Calculate averages for media types
        for media_type in media_type_stats:
            if media_type_stats[media_type]['count'] > 0:
                media_type_stats[media_type]['avg_engagement'] = round(
                    media_type_stats[media_type]['total_engagement'] / 
                    media_type_stats[media_type]['count'], 2
                )
        
        # Find best performing media type based on average engagement
        best_performing_type = None
        if any(stats['count'] > 0 for stats in media_type_stats.values()):
            best_performing_type = max(
                [k for k, v in media_type_stats.items() if v['count'] > 0],
                key=lambda x: media_type_stats[x]['avg_engagement']
            )
        
        return {
            'performance_by_type': media_type_stats,
            'media_type_analysis': media_type_stats,  # Legacy compatibility
            'best_performing_type': best_performing_type,
            'total_types': len([k for k, v in media_type_stats.items() if v['count'] > 0])
        }
    
    def _calculate_optimal_posting_times(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal posting times analysis"""
        posts = base_data['posts']
        
        # Hour-based analysis
        hour_performance = defaultdict(lambda: {'count': 0, 'total_engagement': 0, 'avg_engagement': 0.0})
        
        # Day-based analysis
        day_performance = defaultdict(lambda: {'count': 0, 'total_engagement': 0, 'avg_engagement': 0.0})
        
        for post in posts:
            if post.taken_at_timestamp:
                post_engagement = (post.like_count or 0) + (post.comment_count or 0)
                
                # Hour analysis
                hour = post.taken_at_timestamp.hour
                hour_performance[hour]['count'] += 1
                hour_performance[hour]['total_engagement'] += post_engagement
                
                # Day analysis
                day = post.taken_at_timestamp.strftime('%A')
                day_performance[day]['count'] += 1
                day_performance[day]['total_engagement'] += post_engagement
        
        # Calculate averages
        for hour in hour_performance:
            if hour_performance[hour]['count'] > 0:
                hour_performance[hour]['avg_engagement'] = (
                    hour_performance[hour]['total_engagement'] / hour_performance[hour]['count']
                )
        
        for day in day_performance:
            if day_performance[day]['count'] > 0:
                day_performance[day]['avg_engagement'] = (
                    day_performance[day]['total_engagement'] / day_performance[day]['count']
                )
        
        # Find optimal posting times
        best_hours = sorted(
            hour_performance.items(), 
            key=lambda x: x[1]['avg_engagement'], 
            reverse=True
        )[:3]
        
        best_days = sorted(
            day_performance.items(), 
            key=lambda x: x[1]['avg_engagement'], 
            reverse=True
        )[:3]
        
        # Format for different consumers
        optimal_times_data = [
            {'hour': hour, 'avg_engagement': data['avg_engagement'], 'post_count': data['count']} 
            for hour, data in hour_performance.items() if data['count'] > 0
        ]
        
        return {
            'hour_performance': dict(hour_performance),
            'day_performance': dict(day_performance),
            'best_hours': [
                {'hour': hour, 'avg_engagement': data['avg_engagement'], 'post_count': data['count']} 
                for hour, data in best_hours if data['count'] > 0
            ],
            'best_days': [
                {'day': day, 'avg_engagement': data['avg_engagement'], 'post_count': data['count']} 
                for day, data in best_days if data['count'] > 0
            ],
            'optimal_posting_times': [
                {
                    'hour': f"{hour:02d}:00",
                    'avg_engagement': round(data['avg_engagement'], 2),
                    'posts_count': data['count']
                } for hour, data in best_hours if data['count'] > 0
            ],
            'optimal_posting_analysis': {
                'best_hours': [
                    {'hour': hour, 'avg_engagement': data['avg_engagement'], 'post_count': data['count']} 
                    for hour, data in best_hours if data['count'] > 0
                ],
                'best_days': [
                    {'day': day, 'avg_engagement': data['avg_engagement'], 'post_count': data['count']} 
                    for day, data in best_days if data['count'] > 0
                ],
                'optimal_posting_time': f"{best_hours[0][0]:02d}:00" if best_hours else "Not enough data",
                'time_period_breakdown': self._calculate_time_period_breakdown(posts),
                'favoured_posting_time': self._get_favoured_posting_time(hour_performance)
            }
        }
    
    def _calculate_time_period_breakdown(self, posts: List) -> Dict[str, Any]:
        """Calculate morning/afternoon/evening posting breakdown"""
        periods = {
            'morning': {'count': 0, 'total_engagement': 0, 'percentage': 0.0, 'avg_engagement': 0.0},
            'afternoon': {'count': 0, 'total_engagement': 0, 'percentage': 0.0, 'avg_engagement': 0.0},
            'evening': {'count': 0, 'total_engagement': 0, 'percentage': 0.0, 'avg_engagement': 0.0},
            'night': {'count': 0, 'total_engagement': 0, 'percentage': 0.0, 'avg_engagement': 0.0}
        }
        
        total_posts = len(posts)
        
        for post in posts:
            if post.taken_at_timestamp:
                hour = post.taken_at_timestamp.hour
                engagement = (post.like_count or 0) + (post.comment_count or 0)
                
                if 6 <= hour < 12:  # Morning
                    periods['morning']['count'] += 1
                    periods['morning']['total_engagement'] += engagement
                elif 12 <= hour < 18:  # Afternoon
                    periods['afternoon']['count'] += 1
                    periods['afternoon']['total_engagement'] += engagement
                elif 18 <= hour < 24:  # Evening
                    periods['evening']['count'] += 1
                    periods['evening']['total_engagement'] += engagement
                else:  # Night (0-6 AM)
                    periods['night']['count'] += 1
                    periods['night']['total_engagement'] += engagement
        
        # Calculate percentages and averages
        for period in periods:
            if total_posts > 0:
                periods[period]['percentage'] = round((periods[period]['count'] / total_posts) * 100, 1)
            if periods[period]['count'] > 0:
                periods[period]['avg_engagement'] = round(
                    periods[period]['total_engagement'] / periods[period]['count'], 2
                )
        
        return periods
    
    def _get_favoured_posting_time(self, hour_performance: Dict) -> str:
        """Determine the favoured posting time based on engagement"""
        if not hour_performance:
            return "Morning (9:00 AM - 11:00 AM)"
        
        # Find the hour with highest average engagement
        best_hour = max(hour_performance.items(), key=lambda x: x[1]['avg_engagement'])[0]
        
        if 6 <= best_hour < 12:
            return f"Morning ({best_hour:02d}:00 - {(best_hour+2):02d}:00)"
        elif 12 <= best_hour < 18:
            return f"Afternoon ({best_hour:02d}:00 - {(best_hour+2):02d}:00)"
        elif 18 <= best_hour < 24:
            return f"Evening ({best_hour:02d}:00 - {(best_hour+2):02d}:00)"
        else:
            return f"Night ({best_hour:02d}:00 - {(best_hour+2):02d}:00)"
    
    def get_daily_chart_data(self, username: Optional[str] = None, days: int = 30) -> List[Dict[str, Any]]:
        """Generate daily chart data for time series visualization"""
        from datetime import date
        
        # Get base data
        base_data = self._get_base_data(username, days)
        posts = base_data['posts']
        
        # Create daily buckets
        end_date = date.today()
        daily_data = {}
        
        for i in range(days):
            current_date = end_date - timedelta(days=i)
            daily_data[current_date.isoformat()] = {
                'date': current_date.isoformat(),
                'posts_count': 0,
                'total_engagement': 0,
                'total_likes': 0,
                'total_comments': 0,
                'avg_engagement_per_post': 0
            }
        
        # Aggregate posts by date
        for post in posts:
            if post.taken_at_timestamp:
                post_date = post.taken_at_timestamp.date().isoformat()
                if post_date in daily_data:
                    daily_data[post_date]['posts_count'] += 1
                    daily_data[post_date]['total_engagement'] += (post.like_count or 0) + (post.comment_count or 0)
                    daily_data[post_date]['total_likes'] += (post.like_count or 0)
                    daily_data[post_date]['total_comments'] += (post.comment_count or 0)
        
        # Calculate averages
        for date_key in daily_data:
            day_data = daily_data[date_key]
            if day_data['posts_count'] > 0:
                day_data['avg_engagement_per_post'] = round(
                    day_data['total_engagement'] / day_data['posts_count']
                )
        
        # Return sorted by date
        return sorted(daily_data.values(), key=lambda x: x['date'])
    
    def _calculate_engagement_trends(self, base_data: Dict[str, Any], days: int) -> Dict[str, Any]:
        """Calculate engagement trends over time"""
        posts = base_data['posts']
        start_date = base_data['start_date']
        
        # Daily metrics calculation
        daily_metrics = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            day_posts = [p for p in posts if p.taken_at_timestamp and p.taken_at_timestamp.date() == day.date()]
            
            if day_posts:
                day_engagement = sum((p.like_count or 0) + (p.comment_count or 0) for p in day_posts)
                daily_metrics.append({
                    'date': day.strftime('%Y-%m-%d'),
                    'posts': len(day_posts),
                    'engagement': day_engagement,
                    'avg_engagement': day_engagement / len(day_posts)
                })
            else:
                daily_metrics.append({
                    'date': day.strftime('%Y-%m-%d'),
                    'posts': 0,
                    'engagement': 0,
                    'avg_engagement': 0
                })
        
        # Weekly trend calculation
        recent_week = [m for m in daily_metrics if (datetime.now() - datetime.strptime(m['date'], '%Y-%m-%d')).days <= 7]
        prev_week = [m for m in daily_metrics if 7 < (datetime.now() - datetime.strptime(m['date'], '%Y-%m-%d')).days <= 14]
        
        recent_avg = sum(m['engagement'] for m in recent_week) / len(recent_week) if recent_week else 0
        prev_avg = sum(m['engagement'] for m in prev_week) / len(prev_week) if prev_week else 0
        engagement_trend = ((recent_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
        
        return {
            'daily_metrics': daily_metrics,
            'weekly_trend': {
                'recent_week_avg': recent_avg,
                'previous_week_avg': prev_avg,
                'trend_percentage': engagement_trend
            },
            'engagement_trends': daily_metrics  # Legacy compatibility
        }
    
    def _calculate_performance_insights(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance insights and recommendations"""
        posts = base_data['posts']
        profiles = base_data['profiles']
        
        if not posts:
            return {
                'insights': [],
                'recommendations': [],
                'performance_score': 0,
                'engagement_rate': 0,
                'content_quality': 0
            }
        
        insights = []
        recommendations = []
        
        # Calculate performance metrics
        total_engagement = base_data['total_engagement']
        avg_engagement = total_engagement / len(posts)
        
        # Get follower count for engagement rate calculation
        total_followers = sum(p.followers_count or 0 for p in profiles) if profiles else 1
        engagement_rate = round((avg_engagement / total_followers) * 100, 2) if total_followers > 0 else 0
        
        # Calculate content quality score (0-100 based on multiple factors)
        quality_factors = []
        
        # Factor 1: Consistency (posting frequency)
        posts_per_day = len(posts) / 30  # Assuming 30-day period
        consistency_score = min(100, posts_per_day * 20)  # 5 posts/day = 100%
        quality_factors.append(consistency_score)
        
        # Factor 2: Engagement consistency (variation in engagement)
        engagements = [(p.like_count or 0) + (p.comment_count or 0) for p in posts]
        if engagements and len(engagements) > 1:
            engagement_variance = (max(engagements) - min(engagements)) / avg_engagement if avg_engagement > 0 else 0
            consistency_eng_score = max(0, 100 - (engagement_variance * 20))
            quality_factors.append(consistency_eng_score)
        
        # Factor 3: Content type diversity
        media_types = set(p.media_type for p in posts if p.media_type)
        diversity_score = min(100, len(media_types) * 33.33)  # 3 types = 100%
        quality_factors.append(diversity_score)
        
        # Factor 4: Caption engagement (posts with captions)
        captioned_posts = sum(1 for p in posts if p.caption and len(p.caption.strip()) > 0)
        caption_score = (captioned_posts / len(posts)) * 100 if posts else 0
        quality_factors.append(caption_score)
        
        # Average content quality score
        content_quality = round(sum(quality_factors) / len(quality_factors) if quality_factors else 0)
        
        # Performance score based on engagement rate and content quality
        if engagement_rate > 3:
            performance_score = min(100, 80 + (engagement_rate * 2))
        elif engagement_rate > 1:
            performance_score = min(80, 50 + (engagement_rate * 15))
        else:
            performance_score = min(50, engagement_rate * 25)
        
        performance_score = round((performance_score + content_quality) / 2)
        
        # Generate insights based on data
        if engagement_rate > 3:
            insights.append("Excellent engagement rate - your audience is highly engaged!")
        elif engagement_rate > 1:
            insights.append("Good engagement rate - your content resonates well with your audience")
        elif engagement_rate > 0.5:
            insights.append("Average engagement rate - consider optimizing content strategy")
        else:
            insights.append("Low engagement rate - focus on audience targeting and content quality")
        
        if len(media_types) >= 3:
            insights.append("Great content diversity with multiple media types")
        elif len(media_types) == 2:
            insights.append("Good content variety - consider adding more media types")
        else:
            insights.append("Limited content variety - try mixing different media types")
        
        # Generate recommendations
        if len(posts) < 10:
            recommendations.append("Increase posting frequency for better engagement and reach")
        
        if engagement_rate < 1:
            recommendations.append("Focus on audience interaction and call-to-actions in captions")
            recommendations.append("Use relevant hashtags to increase discoverability")
        
        if content_quality < 50:
            recommendations.append("Improve content consistency and planning")
            recommendations.append("Ensure all posts have meaningful captions")
        
        recommendations.append("Analyze top-performing posts to understand what works best")
        recommendations.append("Monitor optimal posting times for your audience")
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'performance_score': performance_score,
            'engagement_rate': engagement_rate,
            'content_quality': content_quality,
            'avg_engagement': avg_engagement,
            'engagement_category': (
                'Excellent' if engagement_rate > 3 else 
                'Good' if engagement_rate > 1 else 
                'Average' if engagement_rate > 0.5 else 'Low'
            ),
            'quality_factors': {
                'consistency': round(consistency_score),
                'engagement_consistency': round(consistency_eng_score) if 'consistency_eng_score' in locals() else 0,
                'diversity': round(diversity_score),
                'caption_usage': round(caption_score)
            }
        }
    
    def _calculate_story_analytics(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate story-related analytics"""
        stories = base_data['stories']
        
        return {
            'total_active_stories': len(stories),
            'stories_data': [
                {
                    'story_id': story.story_id,
                    'username': story.profile.username if story.profile else 'unknown',
                    'media_type': story.media_type,
                    'posted_at': story.taken_at_timestamp.isoformat() if story.taken_at_timestamp else None,
                    'expires_at': story.expiring_at_timestamp.isoformat() if story.expiring_at_timestamp else None
                }
                for story in stories
            ]
        }
    
    def get_weekly_comparison(self, username: Optional[str] = None, period: str = 'week', 
                            start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get period-over-period comparison data based on most recent data."""
        try:
            # Get all posts for the username, ordered by date
            base_query = MediaPost.query
            if username:
                base_query = base_query.join(Profile).filter(Profile.username == username)
            
            all_posts = base_query.filter(MediaPost.taken_at_timestamp.isnot(None)).order_by(MediaPost.taken_at_timestamp.desc()).limit(200).all()
            
            if not all_posts:
                return {}
            
            # Get the most recent post date and calculate periods based on type
            most_recent_date = all_posts[0].taken_at_timestamp.date()
            
            if period == 'week':
                current_period_start = most_recent_date - timedelta(days=7)
                previous_period_start = current_period_start - timedelta(days=7)
                period_label = 'Week'
            elif period == 'month':
                current_period_start = most_recent_date - timedelta(days=30)
                previous_period_start = current_period_start - timedelta(days=30)
                period_label = 'Month'
            elif period == 'custom' and start_date and end_date:
                # Parse custom dates
                from datetime import datetime as dt
                current_period_end = dt.strptime(end_date, '%Y-%m-%d').date()
                current_period_start = dt.strptime(start_date, '%Y-%m-%d').date()
                
                # Calculate period length and create previous period
                period_length = (current_period_end - current_period_start).days
                previous_period_end = current_period_start
                previous_period_start = previous_period_end - timedelta(days=period_length)
                
                period_label = f'Custom ({start_date} to {end_date})'
            else:  # fallback custom - 14 days each
                current_period_start = most_recent_date - timedelta(days=14)
                previous_period_start = current_period_start - timedelta(days=14)
                period_label = 'Custom (14 days)'
            
            comparison = {}
            
            # Group by username
            if username:
                usernames = [username]
            else:
                usernames = list(set([p.profile.username for p in all_posts]))
            
            for uname in usernames:
                user_posts = [p for p in all_posts if p.profile.username == uname]
                
                # Split posts into two periods
                if period == 'custom' and start_date and end_date:
                    # For custom dates, use exact date ranges
                    current_period_posts = [p for p in user_posts if current_period_start <= p.taken_at_timestamp.date() <= current_period_end]
                    previous_period_posts = [p for p in user_posts if previous_period_start <= p.taken_at_timestamp.date() < current_period_start]
                else:
                    # For week/month, use relative to most recent data
                    current_period_posts = [p for p in user_posts if p.taken_at_timestamp.date() > current_period_start]
                    previous_period_posts = [p for p in user_posts if previous_period_start < p.taken_at_timestamp.date() <= current_period_start]
                
                # Calculate totals for current period
                current_total_engagement = sum((p.like_count or 0) + (p.comment_count or 0) for p in current_period_posts)
                current_total_posts = len(current_period_posts)
                current_avg_engagement = current_total_engagement / current_total_posts if current_total_posts > 0 else 0
                
                # Calculate totals for previous period
                previous_total_engagement = sum((p.like_count or 0) + (p.comment_count or 0) for p in previous_period_posts)
                previous_total_posts = len(previous_period_posts)
                previous_avg_engagement = previous_total_engagement / previous_total_posts if previous_total_posts > 0 else 0
                
                # Calculate percentage changes
                engagement_change = ((current_total_engagement - previous_total_engagement) / previous_total_engagement * 100) if previous_total_engagement > 0 else (100 if current_total_engagement > 0 else 0)
                posts_change = ((current_total_posts - previous_total_posts) / previous_total_posts * 100) if previous_total_posts > 0 else (100 if current_total_posts > 0 else 0)
                
                comparison[uname] = {
                    'current_week': {
                        'total_engagement': current_total_engagement,
                        'total_posts': current_total_posts,
                        'avg_engagement_per_post': round(current_avg_engagement, 2)
                    },
                    'previous_week': {
                        'total_engagement': previous_total_engagement,
                        'total_posts': previous_total_posts,
                        'avg_engagement_per_post': round(previous_avg_engagement, 2)
                    },
                    'changes': {
                        'engagement_change_percent': round(engagement_change, 2),
                        'posts_change_percent': round(posts_change, 2)
                    },
                    'date_range': {
                        'current_period_start': current_period_start.isoformat(),
                        'previous_period_start': previous_period_start.isoformat(),
                        'most_recent_post': most_recent_date.isoformat(),
                        'period_type': period_label
                    }
                }
            
            return comparison
            
        except Exception as e:
            print(f"Error generating period comparison: {e}")
            return {"error": str(e)}
    
    def get_performance_insights(self, username: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get performance insights - wrapper for backward compatibility"""
        analytics = self.get_comprehensive_analytics(
            username=username, 
            days=days,
            include_sections=['posts', 'media_types', 'posting_times', 'performance']
        )
        
        # Transform to match original format
        insights = {}
        
        if username:
            insights[username] = {
                'basic_stats': analytics['posts']['basic_stats'],
                'top_posts': analytics['posts']['top_posts'],
                'bottom_posts': analytics['posts']['bottom_posts'],
                'media_type_analysis': analytics['media_types']['performance_by_type'],
                'optimal_posting_times': analytics['posting_times']['optimal_posting_times'],
                'performance_insights': analytics['performance']
            }
        else:
            # Handle multiple users case
            posts_data = analytics['posts']['posts_data']
            usernames = list(set([p['username'] for p in posts_data]))
            
            for uname in usernames:
                user_posts = [p for p in posts_data if p['username'] == uname]
                user_analytics = self.get_comprehensive_analytics(
                    username=uname, 
                    days=days,
                    include_sections=['posts', 'media_types', 'posting_times', 'performance']
                )
                
                insights[uname] = {
                    'basic_stats': user_analytics['posts']['basic_stats'],
                    'top_posts': user_analytics['posts']['top_posts'],
                    'bottom_posts': user_analytics['posts']['bottom_posts'],
                    'media_type_analysis': user_analytics['media_types']['performance_by_type'],
                    'optimal_posting_times': user_analytics['posting_times']['optimal_posting_times'],
                    'performance_insights': user_analytics['performance']
                }
        
        return insights
    
    def get_analytics_context_for_chatbot(self, username: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get analytics context formatted for chatbot - eliminates chatbot_service redundancy"""
        analytics = self.get_comprehensive_analytics(username=username, days=days)
        
        # Transform to match chatbot expected format
        context = {
            'period_days': days,
            'username_filter': username,
            'total_profiles': analytics['metadata']['total_profiles'],
            'total_posts': analytics['metadata']['total_posts'],
            'total_engagement': analytics['metadata']['total_engagement'],
            'user_profiles': analytics['profiles']['profiles_data'],
            'recent_posts': analytics['posts']['posts_data'],
            'hashtag_analysis': analytics['hashtags'],
            'media_type_analysis': analytics['media_types'],
            'optimal_posting_analysis': analytics['posting_times']['optimal_posting_analysis'],
            'engagement_trends': analytics['engagement_trends']['daily_metrics'],
            'performance_insights': {
                'best_performing_posts': analytics['posts']['best_performing_posts'],
                'worst_performing_posts': analytics['posts']['worst_performing_posts'],
                'engagement_trend_percentage': analytics['engagement_trends']['weekly_trend']['trend_percentage'],
                'recommendations': analytics['performance']['recommendations'],
                'performance_score': analytics['performance']['performance_score']
            }
        }
        
        # Add legacy fields for compatibility
        context.update({
            'total_stories': analytics['stories']['total_active_stories'],
            'avg_likes': analytics['posts']['basic_stats']['avg_likes'],
            'avg_comments': analytics['posts']['basic_stats']['avg_comments'],
            'avg_engagement_per_post': analytics['posts']['basic_stats']['avg_engagement_per_post'],
            'top_post_likes': analytics['posts']['top_post_engagement']
        })
        
        return context

    

    def _calculate_time_period_breakdown(self, posts: List) -> Dict[str, Any]:

        """Calculate morning/afternoon/evening posting breakdown"""

        periods = {

            'morning': {'count': 0, 'total_engagement': 0, 'percentage': 0.0, 'avg_engagement': 0.0},

            'afternoon': {'count': 0, 'total_engagement': 0, 'percentage': 0.0, 'avg_engagement': 0.0},

            'evening': {'count': 0, 'total_engagement': 0, 'percentage': 0.0, 'avg_engagement': 0.0},

            'night': {'count': 0, 'total_engagement': 0, 'percentage': 0.0, 'avg_engagement': 0.0}

        }

        

        total_posts = len(posts)

        

        for post in posts:

            if post.taken_at_timestamp:

                hour = post.taken_at_timestamp.hour

                engagement = (post.like_count or 0) + (post.comment_count or 0)

                

                if 6 <= hour < 12:  # Morning

                    periods['morning']['count'] += 1

                    periods['morning']['total_engagement'] += engagement

                elif 12 <= hour < 18:  # Afternoon

                    periods['afternoon']['count'] += 1

                    periods['afternoon']['total_engagement'] += engagement

                elif 18 <= hour < 24:  # Evening

                    periods['evening']['count'] += 1

                    periods['evening']['total_engagement'] += engagement

                else:  # Night (0-6 AM)

                    periods['night']['count'] += 1

                    periods['night']['total_engagement'] += engagement

        

        # Calculate percentages and averages

        for period in periods:

            if total_posts > 0:

                periods[period]['percentage'] = round((periods[period]['count'] / total_posts) * 100, 1)

            if periods[period]['count'] > 0:

                periods[period]['avg_engagement'] = round(

                    periods[period]['total_engagement'] / periods[period]['count'], 2

                )

        

        return periods

    

    def _get_favoured_posting_time(self, hour_performance: Dict) -> str:

        """Determine the favoured posting time based on engagement"""

        if not hour_performance:

            return "Morning (9:00 AM - 11:00 AM)"

        

        # Find the hour with highest average engagement

        best_hour = max(hour_performance.items(), key=lambda x: x[1]['avg_engagement'])[0]

        

        if 6 <= best_hour < 12:

            return f"Morning ({best_hour:02d}:00 - {(best_hour+2):02d}:00)"

        elif 12 <= best_hour < 18:

            return f"Afternoon ({best_hour:02d}:00 - {(best_hour+2):02d}:00)"

        elif 18 <= best_hour < 24:

            return f"Evening ({best_hour:02d}:00 - {(best_hour+2):02d}:00)"

        else:

            return f"Night ({best_hour:02d}:00 - {(best_hour+2):02d}:00)"

    

    def get_daily_chart_data(self, username: Optional[str] = None, days: int = 30) -> List[Dict[str, Any]]:

        """Generate daily chart data for time series visualization"""

        from datetime import date

        

        # Get base data

        base_data = self._get_base_data(username, days)

        posts = base_data['posts']

        

        # Create daily buckets

        end_date = date.today()

        daily_data = {}

        

        for i in range(days):

            current_date = end_date - timedelta(days=i)

            daily_data[current_date.isoformat()] = {

                'date': current_date.isoformat(),

                'posts_count': 0,

                'total_engagement': 0,

                'total_likes': 0,

                'total_comments': 0,

                'avg_engagement_per_post': 0

            }

        

        # Aggregate posts by date

        for post in posts:

            if post.taken_at_timestamp:

                post_date = post.taken_at_timestamp.date().isoformat()

                if post_date in daily_data:

                    daily_data[post_date]['posts_count'] += 1

                    daily_data[post_date]['total_engagement'] += (post.like_count or 0) + (post.comment_count or 0)

                    daily_data[post_date]['total_likes'] += (post.like_count or 0)

                    daily_data[post_date]['total_comments'] += (post.comment_count or 0)

        

        # Calculate averages

        for date_key in daily_data:

            day_data = daily_data[date_key]

            if day_data['posts_count'] > 0:

                day_data['avg_engagement_per_post'] = round(

                    day_data['total_engagement'] / day_data['posts_count']

                )

        

        # Return sorted by date

        return sorted(daily_data.values(), key=lambda x: x['date'])

    

    def _calculate_engagement_trends(self, base_data: Dict[str, Any], days: int) -> Dict[str, Any]:

        """Calculate engagement trends over time"""

        posts = base_data['posts']

        start_date = base_data['start_date']

        

        # Daily metrics calculation

        daily_metrics = []

        for i in range(days):

            day = start_date + timedelta(days=i)

            day_posts = [p for p in posts if p.taken_at_timestamp and p.taken_at_timestamp.date() == day.date()]

            

            if day_posts:

                day_engagement = sum((p.like_count or 0) + (p.comment_count or 0) for p in day_posts)

                daily_metrics.append({

                    'date': day.strftime('%Y-%m-%d'),

                    'posts': len(day_posts),

                    'engagement': day_engagement,

                    'avg_engagement': day_engagement / len(day_posts)

                })

            else:

                daily_metrics.append({

                    'date': day.strftime('%Y-%m-%d'),

                    'posts': 0,

                    'engagement': 0,

                    'avg_engagement': 0

                })

        

        # Weekly trend calculation

        recent_week = [m for m in daily_metrics if (datetime.now() - datetime.strptime(m['date'], '%Y-%m-%d')).days <= 7]

        prev_week = [m for m in daily_metrics if 7 < (datetime.now() - datetime.strptime(m['date'], '%Y-%m-%d')).days <= 14]

        

        recent_avg = sum(m['engagement'] for m in recent_week) / len(recent_week) if recent_week else 0

        prev_avg = sum(m['engagement'] for m in prev_week) / len(prev_week) if prev_week else 0

        engagement_trend = ((recent_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0

        

        return {

            'daily_metrics': daily_metrics,

            'weekly_trend': {

                'recent_week_avg': recent_avg,

                'previous_week_avg': prev_avg,

                'trend_percentage': engagement_trend

            },

            'engagement_trends': daily_metrics  # Legacy compatibility

        }

    

    def _calculate_performance_insights(self, base_data: Dict[str, Any]) -> Dict[str, Any]:

        """Calculate performance insights and recommendations"""

        posts = base_data['posts']

        profiles = base_data['profiles']

        

        if not posts:

            return {

                'insights': [],

                'recommendations': [],

                'performance_score': 0,

                'engagement_rate': 0,

                'content_quality': 0

            }

        

        insights = []

        recommendations = []

        

        # Calculate performance metrics

        total_engagement = base_data['total_engagement']

        avg_engagement = total_engagement / len(posts)

        

        # Get follower count for engagement rate calculation

        total_followers = sum(p.followers_count or 0 for p in profiles) if profiles else 1

        engagement_rate = round((avg_engagement / total_followers) * 100, 2) if total_followers > 0 else 0

        

        # Calculate content quality score (0-100 based on multiple factors)

        quality_factors = []

        

        # Factor 1: Consistency (posting frequency)

        posts_per_day = len(posts) / 30  # Assuming 30-day period

        consistency_score = min(100, posts_per_day * 20)  # 5 posts/day = 100%

        quality_factors.append(consistency_score)

        

        # Factor 2: Engagement consistency (variation in engagement)

        engagements = [(p.like_count or 0) + (p.comment_count or 0) for p in posts]

        if engagements and len(engagements) > 1:

            engagement_variance = (max(engagements) - min(engagements)) / avg_engagement if avg_engagement > 0 else 0

            consistency_eng_score = max(0, 100 - (engagement_variance * 20))

            quality_factors.append(consistency_eng_score)

        

        # Factor 3: Content type diversity

        media_types = set(p.media_type for p in posts if p.media_type)

        diversity_score = min(100, len(media_types) * 33.33)  # 3 types = 100%

        quality_factors.append(diversity_score)

        

        # Factor 4: Caption engagement (posts with captions)

        captioned_posts = sum(1 for p in posts if p.caption and len(p.caption.strip()) > 0)

        caption_score = (captioned_posts / len(posts)) * 100 if posts else 0

        quality_factors.append(caption_score)

        

        # Average content quality score

        content_quality = round(sum(quality_factors) / len(quality_factors) if quality_factors else 0)

        

        # Performance score based on engagement rate and content quality

        if engagement_rate > 3:

            performance_score = min(100, 80 + (engagement_rate * 2))

        elif engagement_rate > 1:

            performance_score = min(80, 50 + (engagement_rate * 15))

        else:

            performance_score = min(50, engagement_rate * 25)

        

        performance_score = round((performance_score + content_quality) / 2)

        

        # Generate insights based on data

        if engagement_rate > 3:

            insights.append("Excellent engagement rate - your audience is highly engaged!")

        elif engagement_rate > 1:

            insights.append("Good engagement rate - your content resonates well with your audience")

        elif engagement_rate > 0.5:

            insights.append("Average engagement rate - consider optimizing content strategy")

        else:

            insights.append("Low engagement rate - focus on audience targeting and content quality")

        

        if len(media_types) >= 3:

            insights.append("Great content diversity with multiple media types")

        elif len(media_types) == 2:

            insights.append("Good content variety - consider adding more media types")

        else:

            insights.append("Limited content variety - try mixing different media types")

        

        # Generate recommendations

        if len(posts) < 10:

            recommendations.append("Increase posting frequency for better engagement and reach")

        

        if engagement_rate < 1:

            recommendations.append("Focus on audience interaction and call-to-actions in captions")

            recommendations.append("Use relevant hashtags to increase discoverability")

        

        if content_quality < 50:

            recommendations.append("Improve content consistency and planning")

            recommendations.append("Ensure all posts have meaningful captions")

        

        recommendations.append("Analyze top-performing posts to understand what works best")

        recommendations.append("Monitor optimal posting times for your audience")

        

        return {

            'insights': insights,

            'recommendations': recommendations,

            'performance_score': performance_score,

            'engagement_rate': engagement_rate,

            'content_quality': content_quality,

            'avg_engagement': avg_engagement,

            'engagement_category': (

                'Excellent' if engagement_rate > 3 else 

                'Good' if engagement_rate > 1 else 

                'Average' if engagement_rate > 0.5 else 'Low'

            ),

            'quality_factors': {

                'consistency': round(consistency_score),

                'engagement_consistency': round(consistency_eng_score) if 'consistency_eng_score' in locals() else 0,

                'diversity': round(diversity_score),

                'caption_usage': round(caption_score)

            }

        }

    

    def _calculate_story_analytics(self, base_data: Dict[str, Any]) -> Dict[str, Any]:

        """Calculate story-related analytics"""

        stories = base_data['stories']

        

        return {

            'total_active_stories': len(stories),

            'stories_data': [

                {

                    'story_id': story.story_id,

                    'username': story.og_username,

                    'media_type': story.media_type,

                    'posted_at': story.post_datetime_ist.isoformat() if story.post_datetime_ist else None,

                    'expires_at': story.expire_datetime_ist.isoformat() if story.expire_datetime_ist else None

                }

                for story in stories

            ]

        }

    

    def get_weekly_comparison(self, username: Optional[str] = None, period: str = 'week', 

                            start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:

        """Get period-over-period comparison data based on most recent data."""

        try:

            # Get all posts for the username, ordered by date

            base_query = MediaPost.query

            if username:

                base_query = base_query.filter(MediaPost.og_username == username)

            

            all_posts = base_query.filter(MediaPost.taken_at_timestamp.isnot(None)).order_by(MediaPost.taken_at_timestamp.desc()).limit(200).all()

            

            if not all_posts:

                return {}

            

            # Get the most recent post date and calculate periods based on type

            most_recent_date = all_posts[0].taken_at_timestamp.date()

            

            if period == 'week':

                current_period_start = most_recent_date - timedelta(days=7)

                previous_period_start = current_period_start - timedelta(days=7)

                period_label = 'Week'

            elif period == 'month':

                current_period_start = most_recent_date - timedelta(days=30)

                previous_period_start = current_period_start - timedelta(days=30)

                period_label = 'Month'

            elif period == 'custom' and start_date and end_date:

                # Parse custom dates

                from datetime import datetime as dt

                current_period_end = dt.strptime(end_date, '%Y-%m-%d').date()

                current_period_start = dt.strptime(start_date, '%Y-%m-%d').date()

                

                # Calculate period length and create previous period

                period_length = (current_period_end - current_period_start).days

                previous_period_end = current_period_start

                previous_period_start = previous_period_end - timedelta(days=period_length)

                

                period_label = f'Custom ({start_date} to {end_date})'

            else:  # fallback custom - 14 days each

                current_period_start = most_recent_date - timedelta(days=14)

                previous_period_start = current_period_start - timedelta(days=14)

                period_label = 'Custom (14 days)'

            

            comparison = {}

            

            # Group by username

            if username:

                usernames = [username]

            else:

                usernames = list(set([p.og_username for p in all_posts]))

            

            for uname in usernames:

                user_posts = [p for p in all_posts if p.og_username == uname]

                

                # Split posts into two periods

                if period == 'custom' and start_date and end_date:

                    # For custom dates, use exact date ranges

                    current_period_posts = [p for p in user_posts if current_period_start <= p.taken_at_timestamp.date() <= current_period_end]

                    previous_period_posts = [p for p in user_posts if previous_period_start <= p.taken_at_timestamp.date() < current_period_start]

                else:

                    # For week/month, use relative to most recent data

                    current_period_posts = [p for p in user_posts if p.taken_at_timestamp.date() > current_period_start]

                    previous_period_posts = [p for p in user_posts if previous_period_start < p.taken_at_timestamp.date() <= current_period_start]

                

                # Calculate totals for current period

                current_total_engagement = sum((p.like_count or 0) + (p.comment_count or 0) for p in current_period_posts)

                current_total_posts = len(current_period_posts)

                current_avg_engagement = current_total_engagement / current_total_posts if current_total_posts > 0 else 0

                

                # Calculate totals for previous period

                previous_total_engagement = sum((p.like_count or 0) + (p.comment_count or 0) for p in previous_period_posts)

                previous_total_posts = len(previous_period_posts)

                previous_avg_engagement = previous_total_engagement / previous_total_posts if previous_total_posts > 0 else 0

                

                # Calculate percentage changes

                engagement_change = ((current_total_engagement - previous_total_engagement) / previous_total_engagement * 100) if previous_total_engagement > 0 else (100 if current_total_engagement > 0 else 0)

                posts_change = ((current_total_posts - previous_total_posts) / previous_total_posts * 100) if previous_total_posts > 0 else (100 if current_total_posts > 0 else 0)

                

                comparison[uname] = {

                    'current_week': {

                        'total_engagement': current_total_engagement,

                        'total_posts': current_total_posts,

                        'avg_engagement_per_post': round(current_avg_engagement, 2)

                    },

                    'previous_week': {

                        'total_engagement': previous_total_engagement,

                        'total_posts': previous_total_posts,

                        'avg_engagement_per_post': round(previous_avg_engagement, 2)

                    },

                    'changes': {

                        'engagement_change_percent': round(engagement_change, 2),

                        'posts_change_percent': round(posts_change, 2)

                    },

                    'date_range': {

                        'current_period_start': current_period_start.isoformat(),

                        'previous_period_start': previous_period_start.isoformat(),

                        'most_recent_post': most_recent_date.isoformat(),

                        'period_type': period_label

                    }

                }

            

            return comparison

            

        except Exception as e:

            print(f"Error generating period comparison: {e}")

            return {"error": str(e)}

    

    def get_performance_insights(self, username: Optional[str] = None, days: int = 30) -> Dict[str, Any]:

        """Get performance insights - wrapper for backward compatibility"""

        analytics = self.get_comprehensive_analytics(

            username=username, 

            days=days,

            include_sections=['posts', 'media_types', 'posting_times', 'performance']

        )

        

        # Transform to match original format

        insights = {}

        

        if username:

            insights[username] = {

                'basic_stats': analytics['posts']['basic_stats'],

                'top_posts': analytics['posts']['top_posts'],

                'bottom_posts': analytics['posts']['bottom_posts'],

                'media_type_analysis': analytics['media_types']['performance_by_type'],

                'optimal_posting_times': analytics['posting_times']['optimal_posting_times'],

                'performance_insights': analytics['performance']

            }

        else:

            # Handle multiple users case

            posts_data = analytics['posts']['posts_data']

            usernames = list(set([p['username'] for p in posts_data]))

            

            for uname in usernames:

                user_posts = [p for p in posts_data if p['username'] == uname]

                user_analytics = self.get_comprehensive_analytics(

                    username=uname, 

                    days=days,

                    include_sections=['posts', 'media_types', 'posting_times', 'performance']

                )

                

                insights[uname] = {

                    'basic_stats': user_analytics['posts']['basic_stats'],

                    'top_posts': user_analytics['posts']['top_posts'],

                    'bottom_posts': user_analytics['posts']['bottom_posts'],

                    'media_type_analysis': user_analytics['media_types']['performance_by_type'],

                    'optimal_posting_times': user_analytics['posting_times']['optimal_posting_times'],

                    'performance_insights': user_analytics['performance']

                }

        

        return insights

    

    def get_analytics_context_for_chatbot(self, username: Optional[str] = None, days: int = 30) -> Dict[str, Any]:

        """Get analytics context formatted for chatbot - eliminates chatbot_service redundancy"""

        analytics = self.get_comprehensive_analytics(username=username, days=days)

        

        # Transform to match chatbot expected format

        context = {

            'period_days': days,

            'username_filter': username,

            'total_profiles': analytics['metadata']['total_profiles'],

            'total_posts': analytics['metadata']['total_posts'],

            'total_engagement': analytics['metadata']['total_engagement'],

            'user_profiles': analytics['profiles']['profiles_data'],

            'recent_posts': analytics['posts']['posts_data'],

            'hashtag_analysis': analytics['hashtags'],

            'media_type_analysis': analytics['media_types'],

            'optimal_posting_analysis': analytics['posting_times']['optimal_posting_analysis'],

            'engagement_trends': analytics['engagement_trends']['daily_metrics'],

            'performance_insights': {

                'best_performing_posts': analytics['posts']['best_performing_posts'],

                'worst_performing_posts': analytics['posts']['worst_performing_posts'],

                'engagement_trend_percentage': analytics['engagement_trends']['weekly_trend']['trend_percentage'],

                'recommendations': analytics['performance']['recommendations'],

                'performance_score': analytics['performance']['performance_score']

            }

        }

        

        # Add legacy fields for compatibility

        context.update({

            'total_stories': analytics['stories']['total_active_stories'],

            'avg_likes': analytics['posts']['basic_stats']['avg_likes'],

            'avg_comments': analytics['posts']['basic_stats']['avg_comments'],

            'avg_engagement_per_post': analytics['posts']['basic_stats']['avg_engagement_per_post'],

            'top_post_likes': analytics['posts']['top_post_engagement']

        })

        

        return context


