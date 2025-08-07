"""
ChatBot Service for Instagram Analytics Insights
Uses OpenAI GPT for intelligent data analysis and insights
"""
import openai
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import func, desc
from models.database import db, Profile, MediaPost, Story, DailyMetrics
import os


class AnalyticsChatBot:
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-3.5-turbo"  # You can change to gpt-4 for better results
        
        # Conversation memory - stores recent conversations
        self.conversation_memory = {}
        self.max_memory_length = 10  # Keep last 10 exchanges per session
        
    def get_analytics_context(self, username: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """
        Gather comprehensive analytics data including calculated insights from dashboard and analytics pages
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Base queries
            profiles_query = Profile.query
            posts_query = MediaPost.query.filter(MediaPost.post_datetime_ist >= start_date)
            stories_query = Story.query.filter(Story.expire_datetime_ist > datetime.now())
            
            # Apply username filter if specified
            if username:
                profiles_query = profiles_query.filter(Profile.username == username)
                posts_query = posts_query.filter(MediaPost.og_username == username)
                stories_query = stories_query.filter(Story.og_username == username)
            
            # Get profile data
            profiles = profiles_query.all()
            profile_data = []
            for profile in profiles:
                profile_data.append({
                    'username': profile.username,
                    'full_name': profile.full_name,
                    'followers': profile.follower_count,
                    'following': profile.following_count,
                    'posts_count': profile.media_count,
                    'is_verified': profile.is_verified,
                    'is_private': profile.is_private,
                    'bio': getattr(profile, 'bio', ''),
                    'engagement_rate': getattr(profile, 'engagement_rate', 0)
                })
            
            # Get posts data with enhanced analysis
            posts = posts_query.all()
            posts_data = []
            total_engagement = 0
            total_likes = 0
            total_comments = 0
            
            # Media type analysis
            media_type_stats = {}
            
            # Time-based analysis
            hour_performance = {}
            day_performance = {}
            
            # Hashtag analysis
            hashtag_performance = {}
            
            for post in posts:
                post_engagement = (post.like_count or 0) + (post.comment_count or 0)
                total_engagement += post_engagement
                total_likes += (post.like_count or 0)
                total_comments += (post.comment_count or 0)
                
                # Media type analysis
                media_type = post.media_type or 'unknown'
                if media_type not in media_type_stats:
                    media_type_stats[media_type] = {'count': 0, 'total_engagement': 0, 'avg_engagement': 0}
                media_type_stats[media_type]['count'] += 1
                media_type_stats[media_type]['total_engagement'] += post_engagement
                
                # Time-based analysis
                if post.post_datetime_ist:
                    hour = post.post_datetime_ist.hour
                    day = post.post_datetime_ist.strftime('%A')
                    
                    if hour not in hour_performance:
                        hour_performance[hour] = {'count': 0, 'total_engagement': 0}
                    hour_performance[hour]['count'] += 1
                    hour_performance[hour]['total_engagement'] += post_engagement
                    
                    if day not in day_performance:
                        day_performance[day] = {'count': 0, 'total_engagement': 0}
                    day_performance[day]['count'] += 1
                    day_performance[day]['total_engagement'] += post_engagement
                
                posts_data.append({
                    'username': post.og_username,
                    'media_type': post.media_type,
                    'likes': post.like_count or 0,
                    'comments': post.comment_count or 0,
                    'engagement': post_engagement,
                    'posted_at': post.post_datetime_ist.isoformat() if post.post_datetime_ist else None,
                    'caption': post.caption[:200] + '...' if post.caption and len(post.caption) > 200 else post.caption
                })
                
                # Extract hashtags
                if post.caption:
                    import re
                    hashtags = re.findall(r'#\w+', post.caption.lower())
                    for hashtag in hashtags:
                        if hashtag not in hashtag_performance:
                            hashtag_performance[hashtag] = {'count': 0, 'total_engagement': 0}
                        hashtag_performance[hashtag]['count'] += 1
                        hashtag_performance[hashtag]['total_engagement'] += post_engagement
            
            # Calculate averages for media types
            for media_type in media_type_stats:
                if media_type_stats[media_type]['count'] > 0:
                    media_type_stats[media_type]['avg_engagement'] = (
                        media_type_stats[media_type]['total_engagement'] / 
                        media_type_stats[media_type]['count']
                    )
            
            # Calculate averages for time-based analysis
            for hour in hour_performance:
                hour_performance[hour]['avg_engagement'] = (
                    hour_performance[hour]['total_engagement'] / hour_performance[hour]['count']
                )
            
            for day in day_performance:
                day_performance[day]['avg_engagement'] = (
                    day_performance[day]['total_engagement'] / day_performance[day]['count']
                )
            
            # Find optimal posting times
            best_hours = sorted(hour_performance.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)[:3]
            best_days = sorted(day_performance.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)[:3]
            
            # Calculate overall averages
            avg_engagement = total_engagement / len(posts) if posts else 0
            avg_likes = total_likes / len(posts) if posts else 0
            avg_comments = total_comments / len(posts) if posts else 0
            
            # Top hashtags by total engagement
            top_hashtags_total = sorted(
                hashtag_performance.items(),
                key=lambda x: x[1]['total_engagement'],
                reverse=True
            )[:15]
            
            # Top hashtags by average engagement (unique hashtags)
            top_hashtags_avg = sorted(
                hashtag_performance.items(),
                key=lambda x: x[1]['total_engagement'] / x[1]['count'],
                reverse=True
            )[:15]
            
            # Get stories data
            stories = stories_query.all()
            stories_data = len(stories)
            
            # Daily metrics for trend analysis
            daily_metrics = []
            for i in range(days):
                day = start_date + timedelta(days=i)
                day_posts = [p for p in posts if p.post_datetime_ist and p.post_datetime_ist.date() == day.date()]
                
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
            
            # Best and worst performing posts
            best_posts = sorted(posts_data, key=lambda x: x['engagement'], reverse=True)[:10]
            worst_posts = sorted(posts_data, key=lambda x: x['engagement'])[:5]
            
            # Engagement trends
            recent_week = [m for m in daily_metrics if (datetime.now() - datetime.strptime(m['date'], '%Y-%m-%d')).days <= 7]
            prev_week = [m for m in daily_metrics if 7 < (datetime.now() - datetime.strptime(m['date'], '%Y-%m-%d')).days <= 14]
            
            recent_avg = sum(m['engagement'] for m in recent_week) / len(recent_week) if recent_week else 0
            prev_avg = sum(m['engagement'] for m in prev_week) / len(prev_week) if prev_week else 0
            engagement_trend = ((recent_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
            
            return {
                'period_days': days,
                'username_filter': username,
                'total_profiles': len(profiles),
                'total_posts': len(posts),
                'total_stories': stories_data,
                'total_engagement': total_engagement,
                'avg_likes': avg_likes,
                'avg_comments': avg_comments,
                'avg_engagement_per_post': avg_engagement,
                'top_post_likes': max([p['likes'] for p in posts_data], default=0),
                'user_profiles': profile_data,
                'recent_posts': posts_data,
                'hashtag_analysis': {
                    'top_hashtags_by_total_engagement': [
                        {
                            'hashtag': tag.replace('#', ''), 
                            'usage_count': data['count'], 
                            'total_engagement': data['total_engagement'],
                            'avg_engagement': data['total_engagement'] / data['count']
                        } 
                        for tag, data in top_hashtags_total
                    ],
                    'top_hashtags_by_avg_engagement': [
                        {
                            'hashtag': tag.replace('#', ''), 
                            'usage_count': data['count'], 
                            'total_engagement': data['total_engagement'],
                            'avg_engagement': data['total_engagement'] / data['count']
                        } 
                        for tag, data in top_hashtags_avg
                    ],
                    'total_unique_hashtags': len(hashtag_performance)
                },
                'media_type_analysis': {
                    'performance_by_type': media_type_stats,
                    'best_performing_type': max(media_type_stats.items(), key=lambda x: x[1]['avg_engagement'])[0] if media_type_stats else None
                },
                'optimal_posting_analysis': {
                    'best_hours': [{'hour': hour, 'avg_engagement': data['avg_engagement'], 'post_count': data['count']} for hour, data in best_hours],
                    'best_days': [{'day': day, 'avg_engagement': data['avg_engagement'], 'post_count': data['count']} for day, data in best_days],
                    'optimal_posting_time': f"{best_hours[0][0]:02d}:00" if best_hours else "Not enough data"
                },
                'engagement_trends': daily_metrics,
                'performance_insights': {
                    'best_performing_posts': best_posts,
                    'worst_performing_posts': worst_posts,
                    'engagement_trend_percent': engagement_trend,
                    'posting_frequency': len(posts) / days if days > 0 else 0,
                    'engagement_rate': (total_engagement / total_likes * 100) if total_likes > 0 else 0
                },
                'summary': {
                    'period_days': days,
                    'total_posts': len(posts),
                    'total_engagement': total_engagement,
                    'total_profiles': len(profiles)
                }
            }
            
        except Exception as e:
            print(f"Error gathering analytics context: {str(e)}")
            return {'error': f"Failed to gather analytics data: {str(e)}"}
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session"""
        return self.conversation_memory.get(session_id, [])
    
    def add_to_conversation(self, session_id: str, role: str, content: str):
        """Add a message to conversation history"""
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []
        
        self.conversation_memory[session_id].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last N exchanges
        if len(self.conversation_memory[session_id]) > self.max_memory_length * 2:  # *2 for user+assistant pairs
            self.conversation_memory[session_id] = self.conversation_memory[session_id][-self.max_memory_length * 2:]
    
    def generate_system_prompt(self, analytics_data: Dict[str, Any]) -> str:
        """Generate a comprehensive system prompt with analytics context"""
        return f"""You are an expert Instagram Analytics Assistant with deep knowledge of social media marketing, engagement strategies, and data analysis. 

You have access to comprehensive Instagram analytics data and should provide insightful, actionable recommendations based on this data.

CURRENT ANALYTICS CONTEXT:
{json.dumps(analytics_data, indent=2, default=str)}

CAPABILITIES:
- Analyze engagement trends and patterns
- Identify top and bottom performing content
- Provide hashtag strategy recommendations
- Suggest optimal posting times and frequencies
- Compare performance across different accounts
- Identify growth opportunities and areas for improvement
- Explain complex analytics in simple terms

GUIDELINES:
- Always base your responses on the provided data
- Be specific with numbers and percentages when relevant
- Provide actionable insights and recommendations
- Explain your reasoning clearly
- If asked about data not in the context, clearly state the limitation
- Use emojis and formatting to make responses engaging
- Keep responses concise but comprehensive

- Important Tip: Try to deduce the type of post content through the caption and media type, hashtags, and provide insights accordingly, as we cannot describe you the content exactly.

USER CONTEXT:
- Time Period: {analytics_data.get('summary', {}).get('period_days', 30)} days
- Accounts: {'Specific account: ' + analytics_data.get('summary', {}).get('username_filter') if analytics_data.get('summary', {}).get('username_filter') else 'All accounts'}
- Total Posts: {analytics_data.get('summary', {}).get('total_posts', 0)}
- Total Engagement: {analytics_data.get('summary', {}).get('total_engagement', 0)}

Respond naturally and conversationally while being professional and insightful."""

    def chat_sync(self, message: str, session_id: str, username: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """
        Process a chat message and return AI response with analytics insights (synchronous version)
        """
        try:
            # Get analytics context
            analytics_data = self.get_analytics_context(username, days)
            
            if 'error' in analytics_data:
                return {
                    'response': f"I'm sorry, I encountered an error accessing the analytics data: {analytics_data['error']}",
                    'session_id': session_id,
                    'error': True
                }
            
            # Get conversation history
            conversation_history = self.get_conversation_history(session_id)
            
            # Build messages for OpenAI
            messages = [
                {'role': 'system', 'content': self.generate_system_prompt(analytics_data)}
            ]
            
            # Add conversation history (last few exchanges)
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            
            # Add current user message
            messages.append({'role': 'user', 'content': message})
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            ai_response = response.choices[0].message.content
            
            # Store conversation
            self.add_to_conversation(session_id, 'user', message)
            self.add_to_conversation(session_id, 'assistant', ai_response)
            
            return {
                'response': ai_response,
                'session_id': session_id,
                'analytics_summary': analytics_data.get('summary', {}),
                'conversation_length': len(self.conversation_memory.get(session_id, [])),
                'error': False
            }
            
        except Exception as e:
            error_msg = f"I encountered an error processing your request: {str(e)}"
            print(f"ChatBot error: {str(e)}")
            
            return {
                'response': error_msg,
                'session_id': session_id,
                'error': True,
                'error_details': str(e)
            }

    async def chat(self, message: str, session_id: str, username: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """
        Process a chat message and return AI response with analytics insights
        """
        try:
            # Get analytics context
            analytics_data = self.get_analytics_context(username, days)
            
            if 'error' in analytics_data:
                return {
                    'response': f"I'm sorry, I encountered an error accessing the analytics data: {analytics_data['error']}",
                    'session_id': session_id,
                    'error': True
                }
            
            # Get conversation history
            conversation_history = self.get_conversation_history(session_id)
            
            # Build messages for OpenAI
            messages = [
                {'role': 'system', 'content': self.generate_system_prompt(analytics_data)}
            ]
            
            # Add conversation history (last few exchanges)
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            
            # Add current user message
            messages.append({'role': 'user', 'content': message})
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            ai_response = response.choices[0].message.content
            
            # Store conversation
            self.add_to_conversation(session_id, 'user', message)
            self.add_to_conversation(session_id, 'assistant', ai_response)
            
            return {
                'response': ai_response,
                'session_id': session_id,
                'analytics_summary': analytics_data.get('summary', {}),
                'conversation_length': len(self.conversation_memory.get(session_id, [])),
                'error': False
            }
            
        except Exception as e:
            error_msg = f"I encountered an error processing your request: {str(e)}"
            print(f"ChatBot error: {str(e)}")
            
            return {
                'response': error_msg,
                'session_id': session_id,
                'error': True,
                'error_details': str(e)
            }
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversation_memory:
            del self.conversation_memory[session_id]
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        history = self.get_conversation_history(session_id)
        
        if not history:
            return {'message': 'No conversation history found', 'count': 0}
        
        user_messages = [msg for msg in history if msg['role'] == 'user']
        assistant_messages = [msg for msg in history if msg['role'] == 'assistant']
        
        return {
            'total_exchanges': len(user_messages),
            'last_message_time': history[-1]['timestamp'] if history else None,
            'conversation_start': history[0]['timestamp'] if history else None,
            'session_id': session_id
        }


# Global chatbot instance
analytics_chatbot = AnalyticsChatBot()
