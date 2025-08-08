"""
ChatBot Service for Instagram Analytics Insights
Uses OpenAI GPT for intelligent data analysis and insights
Now uses centralized AnalyticsService to eliminate redundancy
"""
import openai
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .analytics_service import AnalyticsService
import os


class AnalyticsChatBot:
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-3.5-turbo"  # You can change to gpt-4 for better results
        
        # Initialize centralized analytics service
        self.analytics_service = AnalyticsService()
        
        # Conversation memory - stores recent conversations
        self.conversation_memory = {}
        self.max_memory_length = 10  # Keep last 10 exchanges per session
        
    def get_analytics_context(self, username: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive analytics data using centralized analytics service
        This eliminates the redundant calculations that were previously here
        """
        try:
            return self.analytics_service.get_analytics_context_for_chatbot(username, days)
        except Exception as e:
            return {'error': f"Failed to gather analytics data: {str(e)}"}
    
    def generate_system_prompt(self, analytics_data: Dict[str, Any]) -> str:
        """
        Generate system prompt with analytics context for the AI assistant
        """
        # Prepare analytics summary for AI context
        total_posts = analytics_data.get('total_posts', 0)
        total_engagement = analytics_data.get('total_engagement', 0)
        avg_engagement = analytics_data.get('avg_engagement_per_post', 0)
        username_filter = analytics_data.get('username_filter', 'all accounts')
        period_days = analytics_data.get('period_days', 30)
        
        # Hashtag insights
        hashtag_analysis = analytics_data.get('hashtag_analysis', {})
        top_hashtags_total = hashtag_analysis.get('top_hashtags_by_total_engagement', [])[:5]
        top_hashtags_avg = hashtag_analysis.get('top_hashtags_by_avg_engagement', [])[:5]
        
        # Media type insights
        media_type_analysis = analytics_data.get('media_type_analysis', {})
        performance_by_type = media_type_analysis.get('performance_by_type', {})
        best_media_type = media_type_analysis.get('best_performing_type', 'unknown')
        
        # Posting time insights
        optimal_posting = analytics_data.get('optimal_posting_analysis', {})
        best_hours = optimal_posting.get('best_hours', [])[:3]
        best_days = optimal_posting.get('best_days', [])[:3]
        
        # Performance insights
        performance_insights = analytics_data.get('performance_insights', {})
        best_posts = performance_insights.get('best_performing_posts', [])[:3]
        recommendations = performance_insights.get('recommendations', [])
        
        system_prompt = f"""
You are an Instagram Analytics Expert Assistant with access to comprehensive data analysis. You help users understand their Instagram performance and provide actionable insights for growth.

CURRENT ANALYTICS CONTEXT:
📊 **Data Overview** (Last {period_days} days for {username_filter})
- Total Posts: {total_posts:,}
- Total Engagement: {total_engagement:,}
- Average Engagement per Post: {avg_engagement:.1f}

📈 **Top Hashtags by Total Engagement:**
{chr(10).join([f"- #{tag['hashtag']}: {tag['total_engagement']:,} total engagement ({tag['usage_count']} uses)" for tag in top_hashtags_total[:3]])}

📈 **Top Hashtags by Average Engagement:**
{chr(10).join([f"- #{tag['hashtag']}: {tag['avg_engagement']:.1f} avg engagement ({tag['usage_count']} uses)" for tag in top_hashtags_avg[:3]])}

📱 **Media Type Performance:**
{chr(10).join([f"- {media_type.title()}: {stats['count']} posts, {stats['avg_engagement']:.1f} avg engagement" for media_type, stats in performance_by_type.items()])}
- Best Performing Type: {best_media_type.title()}

⏰ **Optimal Posting Times (IST):**
{chr(10).join([f"- {hour['hour']}:00 - {hour['avg_engagement']:.1f} avg engagement" for hour in best_hours[:3]])}

📅 **Best Days to Post:**
{chr(10).join([f"- {day['day']}: {day['avg_engagement']:.1f} avg engagement" for day in best_days[:3]])}

🏆 **Top Performing Posts:**
{chr(10).join([f"- {post.get('media_type', 'unknown').title()}: {post['engagement']:,} engagement" for post in best_posts[:2]])}

💡 **Key Recommendations:**
{chr(10).join([f"- {rec}" for rec in recommendations[:3]])}

CAPABILITIES:
- Analyze engagement trends and patterns
- Identify top and bottom performing content  
- Provide hashtag strategy recommendations
- Suggest optimal posting times and frequencies
- Compare performance across different accounts
- Identify growth opportunities and areas for improvement
- Explain complex analytics in simple terms

INSTRUCTIONS:
1. Always base your responses on the provided analytics data
2. Provide specific, actionable recommendations
3. Use emojis and formatting to make responses engaging
4. When asked about data not in context, explain what data is available
5. Focus on growth strategies and performance optimization
6. Keep responses conversational but informative
7. Always mention time periods and date ranges when relevant
8. Provide context for metrics (what's good/bad performance)
9. All times are in IST (Indian Standard Time) unless specified otherwise

Remember: This data covers the last {period_days} days for {username_filter}. Always provide insights based on this specific timeframe and account filter.
"""

        return system_prompt.strip()
    
    def chat_sync(self, message: str, session_id: str, username: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """
        Process user message and return AI response with analytics context
        """
        try:
            # Get analytics context using centralized service
            analytics_context = self.get_analytics_context(username, days)
            
            if 'error' in analytics_context:
                return {
                    'success': False,
                    'error': analytics_context['error'],
                    'response': "I'm sorry, I'm having trouble accessing your analytics data right now. Please try again."
                }
            
            # Generate system prompt with current analytics
            system_prompt = self.generate_system_prompt(analytics_context)
            
            # Manage conversation memory
            if session_id not in self.conversation_memory:
                self.conversation_memory[session_id] = []
            
            # Build conversation history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent conversation history
            for exchange in self.conversation_memory[session_id][-self.max_memory_length:]:
                messages.append({"role": "user", "content": exchange["user"]})
                messages.append({"role": "assistant", "content": exchange["assistant"]})
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=1500,
                temperature=0.7,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content
            
            # Store conversation in memory
            self.conversation_memory[session_id].append({
                "user": message,
                "assistant": ai_response,
                "timestamp": datetime.now().isoformat(),
                "username_filter": username,
                "days_filter": days
            })
            
            # Limit conversation memory
            if len(self.conversation_memory[session_id]) > self.max_memory_length:
                self.conversation_memory[session_id] = self.conversation_memory[session_id][-self.max_memory_length:]
            
            # Prepare analytics summary for response
            analytics_summary = {
                'period_days': analytics_context.get('period_days', days),
                'username_filter': analytics_context.get('username_filter', username),
                'total_posts': analytics_context.get('total_posts', 0),
                'total_engagement': analytics_context.get('total_engagement', 0),
                'avg_engagement': analytics_context.get('avg_engagement_per_post', 0),
                'top_hashtag': (analytics_context.get('hashtag_analysis', {})
                               .get('top_hashtags_by_total_engagement', [{}])[0]
                               .get('hashtag', 'N/A') if analytics_context.get('hashtag_analysis', {})
                               .get('top_hashtags_by_total_engagement') else 'N/A'),
                'best_media_type': analytics_context.get('media_type_analysis', {}).get('best_performing_type', 'N/A'),
                'optimal_hour': (analytics_context.get('optimal_posting_analysis', {})
                               .get('best_hours', [{}])[0]
                               .get('hour', 'N/A') if analytics_context.get('optimal_posting_analysis', {})
                               .get('best_hours') else 'N/A')
            }
            
            return {
                'success': True,
                'response': ai_response,
                'analytics_summary': analytics_summary,
                'analytics_context': analytics_context,  # Full context for frontend display
                'conversation_length': len(self.conversation_memory[session_id]),
                'model_used': self.model,
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
        except Exception as e:
            error_msg = f"ChatBot Error: {str(e)}"
            print(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again or contact support if the issue persists."
            }
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        return self.conversation_memory.get(session_id, [])
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        if session_id in self.conversation_memory:
            del self.conversation_memory[session_id]
            return True
        return False
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.conversation_memory.keys())
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about active sessions"""
        total_sessions = len(self.conversation_memory)
        total_exchanges = sum(len(history) for history in self.conversation_memory.values())
        
        return {
            'total_active_sessions': total_sessions,
            'total_conversation_exchanges': total_exchanges,
            'average_exchanges_per_session': total_exchanges / total_sessions if total_sessions > 0 else 0,
            'memory_usage_mb': len(str(self.conversation_memory)) / (1024 * 1024)
        }
