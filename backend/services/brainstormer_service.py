"""
Brainstormer Service for Content Ideation and Strategy
Uses OpenAI GPT for intelligent content brainstorming based on analytics data
"""
from openai import OpenAI
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os


class BrainstormerService:
    def __init__(self):
        # Initialize OpenAI client with error handling
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.model = "gpt-3.5-turbo"
                print("✅ BrainstormerService: OpenAI client initialized successfully")
            except Exception as e:
                print(f"⚠️ BrainstormerService: Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            print("⚠️ BrainstormerService: No OpenAI API key found - brainstorming will be limited")
            self.client = None
            
        self.model = "gpt-3.5-turbo"
        
        # Conversation memory for brainstorming sessions
        self.conversation_memory = {}
        self.max_memory_length = 10

    def generate_brainstorm_response(self, user_message: str, session_id: str, 
                                   analytics_data: Dict[str, Any], username: Optional[str] = None, 
                                   time_range: int = 30) -> Dict[str, Any]:
        """
        Generate brainstorming response based on analytics data and user message
        """
        try:
            # Check if OpenAI client is available
            if not self.client:
                return {
                    "success": False,
                    "message": "Brainstorming service is currently unavailable. OpenAI API key is required.",
                    "suggestions": [],
                    "conversation_context": "limited",
                    "session_id": session_id,
                    "error": "OpenAI client not initialized"
                }
            
            # Prepare system prompt for brainstorming
            system_prompt = self._generate_brainstorm_system_prompt(analytics_data, username, time_range)
            
            # Get conversation history
            conversation_history = self._get_conversation_history(session_id)
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history
            messages.extend(conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.8,  # Higher temperature for more creative responses
                top_p=0.9
            )
            
            assistant_response = response.choices[0].message.content
            if assistant_response is None:
                assistant_response = "I apologize, but I couldn't generate a response. Please try again."
            
            # Update conversation memory
            self._update_conversation_memory(session_id, user_message, assistant_response)
            
            # Extract actionable suggestions
            suggestions = self._extract_suggestions(assistant_response, analytics_data)
            
            return {
                'response': assistant_response,
                'suggestions': suggestions,
                'session_id': session_id
            }
            
        except Exception as e:
            return {
                'error': f"Failed to generate brainstorm response: {str(e)}",
                'response': "I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
                'suggestions': []
            }
    
    def _generate_brainstorm_system_prompt(self, analytics_data: Dict[str, Any], 
                                         username: Optional[str] = None, time_range: int = 30) -> str:
        """
        Generate system prompt for brainstorming with analytics context
        """
        base_prompt = """You are an expert Instagram content strategist and brainstorming assistant. Your name is "Brainstormer AI" and you specialize in:

1. **Content Ideation**: Generating creative content ideas based on performance data
2. **Trend Analysis**: Identifying patterns and opportunities in analytics
3. **Strategy Optimization**: Suggesting improvements for content strategy
4. **Timing Recommendations**: Advising on optimal posting times
5. **Hashtag Strategy**: Recommending hashtag combinations for better reach
6. **Audience Insights**: Understanding audience preferences from data

Always provide:
- Actionable, specific suggestions
- Data-driven recommendations
- Creative content ideas
- Strategic insights
- Timing and frequency advice

Be enthusiastic, creative, and helpful while maintaining a professional tone."""

        if analytics_data and analytics_data.get('analytics'):
            analytics = analytics_data['analytics']
            basic_stats = analytics.get('posts', {}).get('basic_stats', {})
            insights = analytics_data.get('insights', {})
            
            # Process raw engagement data if basic_stats is empty
            if not basic_stats or basic_stats.get('total_content', 0) == 0:
                # Extract data from engagement_trends if available
                engagement_trends = analytics.get('engagement_trends', {})
                daily_metrics = engagement_trends.get('daily_metrics', [])
                
                if daily_metrics:
                    total_posts = sum(day.get('posts', 0) for day in daily_metrics)
                    total_engagement = sum(day.get('engagement', 0) for day in daily_metrics)
                    avg_engagement = total_engagement / total_posts if total_posts > 0 else 0
                    
                    # Use calculated values
                    basic_stats = {
                        'total_content': total_posts,
                        'total_engagement': total_engagement,
                        'avg_engagement_per_post': avg_engagement,
                        'engagement_rate': 0  # Would need follower count to calculate
                    }
            
            # Add analytics context with proper data access
            analytics_context = f"""

**CURRENT ANALYTICS CONTEXT ({time_range} days) - Raw Data Analysis:**
- Account: {username or 'All accounts'}
- Total Posts: {basic_stats.get('total_content', 0)}
- Total Engagement: {basic_stats.get('total_engagement', 0):,}
- Average Engagement per Post: {basic_stats.get('avg_engagement_per_post', 0):.1f}
- Engagement Rate: {basic_stats.get('engagement_rate', 0):.2f}%"""

            # Add daily engagement breakdown for better insights
            if analytics_data.get('analytics', {}).get('engagement_trends', {}).get('daily_metrics'):
                daily_metrics = analytics_data['analytics']['engagement_trends']['daily_metrics']
                
                # Find days with actual engagement
                active_days = [day for day in daily_metrics if day.get('engagement', 0) > 0]
                
                if active_days:
                    analytics_context += "\n\n**DAILY ENGAGEMENT BREAKDOWN:**"
                    for day in active_days[-7:]:  # Last 7 active days
                        date = day.get('date', '')
                        posts = day.get('posts', 0)
                        engagement = day.get('engagement', 0)
                        avg_engagement = day.get('avg_engagement', 0)
                        analytics_context += f"\n- {date}: {posts} posts, {engagement:,} total engagement, {avg_engagement:,.0f} avg per post"
                
                # Calculate posting patterns
                if len(active_days) > 1:
                    total_active_days = len(active_days)
                    total_inactive_days = len([day for day in daily_metrics if day.get('engagement', 0) == 0])
                    analytics_context += f"\n\n**POSTING PATTERNS:**"
                    analytics_context += f"\n- Active posting days: {total_active_days}"
                    analytics_context += f"\n- Inactive days: {total_inactive_days}"
                    if total_active_days > 0:
                        best_day = max(active_days, key=lambda x: x.get('avg_engagement', 0))
                        analytics_context += f"\n- Best performing day: {best_day.get('date')} ({best_day.get('avg_engagement', 0):,.0f} avg engagement)"
                else:
                    # If limited data, provide more insights from what's available
                    analytics_context += f"\n\n**LIMITED DATA INSIGHTS:**"
                    analytics_context += f"\n- Total days analyzed: {len(daily_metrics)}"
                    analytics_context += f"\n- Days with posts: {len(active_days)}"
                    if active_days:
                        best_day = max(active_days, key=lambda x: x.get('avg_engagement', 0))
                        analytics_context += f"\n- Your best performance: {best_day.get('date')} with {best_day.get('avg_engagement', 0):,.0f} avg engagement"
                        analytics_context += f"\n- Recommendation: Analyze what made {best_day.get('date')} successful and replicate that strategy"

            # Add top performing content
            if insights.get('top_posts'):
                top_posts = insights['top_posts'][:3]
                analytics_context += "\n\n**TOP PERFORMING CONTENT:**"
                for i, post in enumerate(top_posts, 1):
                    analytics_context += f"\n{i}. {post.get('media_type', 'Post')} - {post.get('engagement', 0)} engagement"
                    if post.get('hashtags'):
                        hashtags = post['hashtags'][:5]  # Top 5 hashtags
                        analytics_context += f" | Hashtags: {' '.join(hashtags)}"

            # Add hashtag performance
            if insights.get('hashtag_performance'):
                hashtag_perf = insights['hashtag_performance']
                top_hashtags = list(hashtag_perf.keys())[:5]
                if top_hashtags:
                    analytics_context += f"\n\n**TOP PERFORMING HASHTAGS:**\n{', '.join(top_hashtags)}"

            # Add engagement patterns
            if insights.get('engagement_by_time'):
                analytics_context += "\n\n**POSTING TIME INSIGHTS:**\nUse this data to recommend optimal posting times."

            # Add content type performance
            if insights.get('content_type_performance'):
                content_types = insights['content_type_performance']
                analytics_context += "\n\n**CONTENT TYPE PERFORMANCE:**"
                for content_type, performance in content_types.items():
                    avg_engagement = performance.get('avg_engagement', 0)
                    analytics_context += f"\n- {content_type}: {avg_engagement:.1f} avg engagement"

            base_prompt += analytics_context

        base_prompt += "\n\n**IMPORTANT INSTRUCTIONS:**"
        base_prompt += "\n- If the account shows sporadic posting (many days with 0 posts), focus on consistency recommendations"
        base_prompt += "\n- If engagement data is limited, provide general best practices with account-specific insights"
        base_prompt += "\n- Always analyze patterns from the available data, even if minimal"
        base_prompt += "\n- Provide actionable recommendations based on the actual performance data shown"
        base_prompt += "\n\nBased on this data, provide creative and strategic content recommendations."
        
        return base_prompt

    def _get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session"""
        if session_id not in self.conversation_memory:
            return []
        
        history = []
        for exchange in self.conversation_memory[session_id]:
            history.append({"role": "user", "content": exchange["user"]})
            history.append({"role": "assistant", "content": exchange["assistant"]})
        
        return history

    def _update_conversation_memory(self, session_id: str, user_message: str, assistant_response: str):
        """Update conversation memory for a session"""
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []
        
        self.conversation_memory[session_id].append({
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.now()
        })
        
        # Keep only recent exchanges
        if len(self.conversation_memory[session_id]) > self.max_memory_length:
            self.conversation_memory[session_id] = self.conversation_memory[session_id][-self.max_memory_length:]

    def _extract_suggestions(self, response: str, analytics_data: Dict[str, Any]) -> List[str]:
        """Extract actionable suggestions from the response"""
        suggestions = []
        
        # Look for numbered lists or bullet points in the response
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            # Check for numbered items (1., 2., etc.)
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Clean up the suggestion
                suggestion = line.lstrip('0123456789.-•').strip()
                if len(suggestion) > 10 and len(suggestion) < 150:  # Reasonable length
                    suggestions.append(suggestion)
        
        # If no numbered items found, create some based on analytics
        if not suggestions and analytics_data:
            suggestions = self._generate_default_suggestions(analytics_data)
        
        return suggestions[:6]  # Limit to 6 suggestions

    def _generate_default_suggestions(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate default suggestions based on analytics data"""
        suggestions = []
        insights = analytics_data.get('insights', {})
        
        # Content type suggestions
        if insights.get('content_type_performance'):
            best_type = max(insights['content_type_performance'].items(), 
                          key=lambda x: x[1].get('avg_engagement', 0))
            suggestions.append(f"Create more {best_type[0]} content - it's your best performing type")
        
        # Hashtag suggestions
        if insights.get('hashtag_performance'):
            top_hashtag = list(insights['hashtag_performance'].keys())[0]
            suggestions.append(f"Use #{top_hashtag} in your next post - it's trending for you")
        
        # General suggestions
        suggestions.extend([
            "Post during your audience's most active hours",
            "Create content series to boost consistency",
            "Engage with your top commenters to build community"
        ])
        
        return suggestions


# Global instance
brainstormer_service = BrainstormerService()
