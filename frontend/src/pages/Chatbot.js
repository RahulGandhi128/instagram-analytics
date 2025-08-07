import React, { useState, useEffect, useRef } from 'react';
import { Bot, Send, Trash2, Settings } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { chatbotAPI } from '../services/chatbotAPI';
import { useUsernames } from '../hooks/useUsernames';

const Chatbot = ({ showNotification }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [selectedUsername, setSelectedUsername] = useState('');
  const [timeRange, setTimeRange] = useState(30);
  const [analyticsContext, setAnalyticsContext] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [showAnalyticsDialog, setShowAnalyticsDialog] = useState(false);
  const [selectedAnalyticsData, setSelectedAnalyticsData] = useState(null);
  const messagesEndRef = useRef(null);
  
  const { usernames: allUsernames } = useUsernames();

  // Generate session ID on component mount
  useEffect(() => {
    const newSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
    
    // Add welcome message
    setMessages([{
      id: Date.now(),
      type: 'assistant',
      content: `👋 Hello! I'm your Instagram Analytics Assistant. I can help you analyze your Instagram data, identify trends, and provide actionable insights.

🔍 **What I can help you with:**
• Analyze engagement trends and patterns
• Identify top and bottom performing content
• Provide hashtag strategy recommendations
• Suggest optimal posting strategies
• Compare performance across accounts
• Explain analytics in simple terms

📊 **Current Context:** ${selectedUsername || 'All accounts'} - Last ${timeRange} days

💬 **Try asking:**
- "What are my top performing posts?"
- "How is my engagement trending?"
- "Which hashtags work best?"
- "What insights do you see in my data?"

Feel free to ask me anything about your Instagram analytics!`,
      timestamp: new Date().toISOString()
    }]);
  }, [selectedUsername, timeRange]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load analytics context when filters change
  useEffect(() => {
    const loadAnalyticsContext = async () => {
      try {
        const response = await chatbotAPI.getAnalyticsContext(selectedUsername, timeRange);
        if (response.success) {
          setAnalyticsContext(response.data);
        }
      } catch (error) {
        console.error('Failed to load analytics context:', error);
      }
    };

    if (sessionId) {
      loadAnalyticsContext();
    }
  }, [selectedUsername, timeRange, sessionId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatbotAPI.sendMessage(
        userMessage.content,
        sessionId,
        selectedUsername,
        timeRange
      );

      if (response.success) {
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: response.data.response,
          timestamp: new Date().toISOString(),
          analytics_summary: response.data.analytics_summary
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(response.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `I'm sorry, I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      showNotification('Error sending message to chatbot', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const clearConversation = async () => {
    if (!window.confirm('Are you sure you want to clear the conversation history?')) {
      return;
    }

    try {
      await chatbotAPI.clearHistory(sessionId);
      setMessages([]);
      showNotification('Conversation cleared successfully', 'success');
      
      // Add welcome message again
      setTimeout(() => {
        setMessages([{
          id: Date.now(),
          type: 'assistant',
          content: `👋 New conversation started! I'm ready to help you analyze your Instagram data.

📊 **Current Context:** ${selectedUsername || 'All accounts'} - Last ${timeRange} days

What would you like to know about your Instagram analytics?`,
          timestamp: new Date().toISOString()
        }]);
      }, 100);
    } catch (error) {
      console.error('Failed to clear conversation:', error);
      showNotification('Failed to clear conversation', 'error');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content) => {
    // Simple formatting for better readability
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br/>');
  };

  const getSuggestedQuestions = () => {
    const baseQuestions = [
      "What are my top performing posts?",
      "How is my engagement trending?",
      "Which hashtags should I use?",
      "What's my best posting time?",
      "Compare my accounts performance",
      "Show me my analytics summary"
    ];

    if (selectedUsername) {
      return [
        `How is ${selectedUsername} performing?`,
        `What are ${selectedUsername}'s best posts?`,
        `Analyze ${selectedUsername}'s engagement`,
        ...baseQuestions.slice(3)
      ];
    }

    return baseQuestions;
  };

  const handleAnalyticsContextClick = async (analyticsData) => {
    try {
      // If analyticsData is not provided, fetch current analytics context
      if (!analyticsData) {
        const response = await chatbotAPI.getAnalyticsContext({
          username: selectedUsername,
          days: timeRange
        });
        
        if (response.success) {
          setSelectedAnalyticsData(response.data);
        } else {
          showNotification('Failed to load analytics context', 'error');
          return;
        }
      } else {
        setSelectedAnalyticsData(analyticsData);
      }
      
      setShowAnalyticsDialog(true);
    } catch (error) {
      console.error('Error loading analytics context:', error);
      showNotification('Failed to load analytics context', 'error');
    }
  };

  const convertToMarkdown = (data) => {
    if (!data) return '**No data available**';

    let markdown = '';

    // Summary Section
    if (data.summary || data.period_days || data.total_posts) {
      markdown += '## 📊 Analytics Summary\n\n';
      markdown += `- **Period:** ${data.period_days || data.summary?.period_days || 'N/A'} days\n`;
      markdown += `- **Total Posts:** ${data.total_posts || data.summary?.total_posts || 0}\n`;
      markdown += `- **Total Engagement:** ${(data.total_engagement || data.summary?.total_engagement || 0).toLocaleString()}\n`;
      markdown += `- **Accounts:** ${data.total_profiles || data.summary?.total_profiles || data.user_profiles?.length || 0}\n\n`;
    }

    // User Profiles
    if (data.user_profiles && data.user_profiles.length > 0) {
      markdown += '## 👤 User Profiles\n\n';
      data.user_profiles.forEach((profile, index) => {
        markdown += `### ${index + 1}. @${profile.username}\n`;
        markdown += `- **Followers:** ${profile.followers?.toLocaleString() || 'N/A'}\n`;
        markdown += `- **Following:** ${profile.following?.toLocaleString() || 'N/A'}\n`;
        markdown += `- **Posts:** ${profile.posts_count || 'N/A'}\n`;
        if (profile.bio) markdown += `- **Bio:** ${profile.bio}\n`;
        markdown += '\n';
      });
    }

    // Recent Posts
    if (data.recent_posts && data.recent_posts.length > 0) {
      markdown += '## 📝 Recent Posts\n\n';
      data.recent_posts.slice(0, 20).forEach((post, index) => {
        markdown += `### ${index + 1}. Post by @${post.username}\n`;
        markdown += `- **Date:** ${new Date(post.posted_at).toLocaleDateString()}\n`;
        markdown += `- **Likes:** ${post.likes?.toLocaleString() || 0}\n`;
        markdown += `- **Comments:** ${post.comments?.toLocaleString() || 0}\n`;
        markdown += `- **Media Type:** ${post.media_type || 'Unknown'}\n`;
        if (post.caption) {
          const caption = post.caption.length > 200 ? post.caption.substring(0, 200) + '...' : post.caption;
          markdown += `- **Caption:** ${caption}\n`;
        }
        markdown += '\n';
      });
    }

    // Hashtag Analysis - Top by Total Engagement
    if (data.hashtag_analysis?.top_hashtags_by_total_engagement && data.hashtag_analysis.top_hashtags_by_total_engagement.length > 0) {
      markdown += '## #️⃣ Top Hashtags by Total Engagement\n\n';
      markdown += '| Hashtag | Usage Count | Total Engagement | Avg Engagement |\n';
      markdown += '|---------|-------------|------------------|----------------|\n';
      data.hashtag_analysis.top_hashtags_by_total_engagement.slice(0, 10).forEach(hashtag => {
        markdown += `| #${hashtag.hashtag} | ${hashtag.usage_count} | ${hashtag.total_engagement?.toLocaleString() || 0} | ${hashtag.avg_engagement?.toFixed(1) || 0} |\n`;
      });
      markdown += '\n';
    }

    // Hashtag Analysis - Top by Average Engagement
    if (data.hashtag_analysis?.top_hashtags_by_avg_engagement && data.hashtag_analysis.top_hashtags_by_avg_engagement.length > 0) {
      markdown += '## ⭐ Top Hashtags by Average Engagement\n\n';
      markdown += '| Hashtag | Usage Count | Total Engagement | Avg Engagement |\n';
      markdown += '|---------|-------------|------------------|----------------|\n';
      data.hashtag_analysis.top_hashtags_by_avg_engagement.slice(0, 10).forEach(hashtag => {
        markdown += `| #${hashtag.hashtag} | ${hashtag.usage_count} | ${hashtag.total_engagement?.toLocaleString() || 0} | ${hashtag.avg_engagement?.toFixed(1) || 0} |\n`;
      });
      markdown += '\n';
    }

    // Legacy hashtag support (fallback)
    if (!data.hashtag_analysis?.top_hashtags_by_total_engagement && data.hashtag_analysis?.top_hashtags && data.hashtag_analysis.top_hashtags.length > 0) {
      markdown += '## #️⃣ Top Hashtags\n\n';
      markdown += '| Hashtag | Usage Count | Total Engagement |\n';
      markdown += '|---------|-------------|------------------|\n';
      data.hashtag_analysis.top_hashtags.forEach(hashtag => {
        markdown += `| #${hashtag.hashtag} | ${hashtag.usage_count} | ${hashtag.total_engagement?.toLocaleString() || 0} |\n`;
      });
      markdown += '\n';
    }

    // Engagement Trends
    if (data.engagement_trends && data.engagement_trends.length > 0) {
      markdown += '## 📈 Engagement Trends\n\n';
      data.engagement_trends.forEach((trend, index) => {
        markdown += `### Trend ${index + 1}\n`;
        markdown += `- **Date:** ${trend.date}\n`;
        markdown += `- **Engagement:** ${trend.engagement?.toLocaleString() || 0}\n`;
        markdown += `- **Posts:** ${trend.posts || 0}\n\n`;
      });
    }

    // Performance Metrics
    if (data.avg_likes || data.avg_comments || data.top_post_likes) {
      markdown += '## 🎯 Performance Metrics\n\n';
      if (data.avg_likes) markdown += `- **Average Likes:** ${data.avg_likes.toFixed(1)}\n`;
      if (data.avg_comments) markdown += `- **Average Comments:** ${data.avg_comments.toFixed(1)}\n`;
      if (data.top_post_likes) markdown += `- **Best Performing Post:** ${data.top_post_likes.toLocaleString()} likes\n`;
      markdown += '\n';
    }

    // Media Type Analysis
    if (data.media_type_analysis?.performance_by_type) {
      markdown += '## 📱 Media Type Performance\n\n';
      const mediaTypes = Object.keys(data.media_type_analysis.performance_by_type);
      if (mediaTypes.length > 0) {
        markdown += '| Media Type | Posts | Total Engagement | Avg Engagement |\n';
        markdown += '|------------|-------|------------------|----------------|\n';
        mediaTypes.forEach(type => {
          const stats = data.media_type_analysis.performance_by_type[type];
          markdown += `| ${type} | ${stats.count} | ${stats.total_engagement?.toLocaleString() || 0} | ${stats.avg_engagement?.toFixed(1) || 0} |\n`;
        });
        markdown += '\n';
        if (data.media_type_analysis.best_performing_type) {
          markdown += `**Best Performing Type:** ${data.media_type_analysis.best_performing_type}\n\n`;
        }
      }
    }

    // Optimal Posting Analysis
    if (data.optimal_posting_analysis) {
      markdown += '## ⏰ Optimal Posting Times\n\n';
      
      if (data.optimal_posting_analysis.best_hours && data.optimal_posting_analysis.best_hours.length > 0) {
        markdown += '### Best Hours to Post\n';
        markdown += '| Hour | Avg Engagement | Posts Count |\n';
        markdown += '|------|----------------|-------------|\n';
        data.optimal_posting_analysis.best_hours.forEach(hour => {
          markdown += `| ${hour.hour}:00 | ${hour.avg_engagement?.toFixed(1) || 0} | ${hour.post_count} |\n`;
        });
        markdown += '\n';
      }

      if (data.optimal_posting_analysis.best_days && data.optimal_posting_analysis.best_days.length > 0) {
        markdown += '### Best Days to Post\n';
        markdown += '| Day | Avg Engagement | Posts Count |\n';
        markdown += '|-----|----------------|-------------|\n';
        data.optimal_posting_analysis.best_days.forEach(day => {
          markdown += `| ${day.day} | ${day.avg_engagement?.toFixed(1) || 0} | ${day.post_count} |\n`;
        });
        markdown += '\n';
      }

      if (data.optimal_posting_analysis.optimal_posting_time) {
        markdown += `**Optimal Posting Time:** ${data.optimal_posting_analysis.optimal_posting_time}\n\n`;
      }
    }

    // Performance Insights
    if (data.performance_insights) {
      markdown += '## 🚀 Performance Insights\n\n';
      
      if (data.performance_insights.engagement_trend_percent) {
        markdown += `- **Engagement Trend:** ${data.performance_insights.engagement_trend_percent > 0 ? '📈' : '📉'} ${data.performance_insights.engagement_trend_percent.toFixed(1)}%\n`;
      }
      if (data.performance_insights.posting_frequency) {
        markdown += `- **Posting Frequency:** ${data.performance_insights.posting_frequency.toFixed(1)} posts/day\n`;
      }
      if (data.performance_insights.engagement_rate) {
        markdown += `- **Engagement Rate:** ${data.performance_insights.engagement_rate.toFixed(1)}%\n`;
      }

      if (data.performance_insights.best_performing_posts && data.performance_insights.best_performing_posts.length > 0) {
        markdown += '\n### 🏆 Top Performing Posts\n';
        data.performance_insights.best_performing_posts.slice(0, 5).forEach((post, index) => {
          markdown += `${index + 1}. **${post.engagement?.toLocaleString() || 0}** engagement by @${post.username} (${post.media_type})\n`;
        });
      }
      markdown += '\n';
    }

    // Additional Data
    const excludeKeys = ['user_profiles', 'recent_posts', 'hashtag_analysis', 'engagement_trends', 'summary', 'period_days', 'total_posts', 'total_engagement', 'total_profiles', 'avg_likes', 'avg_comments', 'top_post_likes', 'media_type_analysis', 'optimal_posting_analysis', 'performance_insights'];
    const additionalData = Object.keys(data).filter(key => !excludeKeys.includes(key));
    
    if (additionalData.length > 0) {
      markdown += '## 🔧 Additional Data\n\n';
      additionalData.forEach(key => {
        const value = data[key];
        if (value !== null && value !== undefined) {
          if (typeof value === 'object') {
            markdown += `### ${key}\n\`\`\`json\n${JSON.stringify(value, null, 2)}\n\`\`\`\n\n`;
          } else {
            markdown += `- **${key}:** ${value}\n`;
          }
        }
      });
    }

    return markdown;
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-instagram-purple to-instagram-pink rounded-lg">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Analytics Assistant</h1>
              <p className="text-sm text-gray-500">
                AI-powered insights for your Instagram data
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              title="Settings"
            >
              <Settings className="w-5 h-5" />
            </button>
            <button
              onClick={clearConversation}
              className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50"
              title="Clear conversation"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Analytics Context</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  Account Filter
                </label>
                <select
                  value={selectedUsername}
                  onChange={(e) => setSelectedUsername(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-instagram-purple"
                >
                  <option value="">All Accounts</option>
                  {allUsernames.map(username => (
                    <option key={username} value={username}>{username}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  Time Period
                </label>
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-instagram-purple"
                >
                  <option value={7}>Last 7 days</option>
                  <option value={14}>Last 14 days</option>
                  <option value={30}>Last 30 days</option>
                  <option value={90}>Last 90 days</option>
                </select>
              </div>
            </div>
            
            {analyticsContext && (
              <div 
                className="mt-3 p-2 bg-blue-50 rounded border border-blue-200 cursor-pointer hover:bg-blue-100 transition-colors duration-200"
                onClick={() => handleAnalyticsContextClick(analyticsContext)}
                title="Click to view detailed analytics context"
              >
                <div className="flex items-center justify-between">
                  <div className="text-xs text-blue-700">
                    📊 Context: {analyticsContext.summary?.total_posts || 0} posts, 
                    {analyticsContext.summary?.total_engagement || 0} total engagement
                  </div>
                  <div className="text-blue-600 hover:text-blue-800">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                </div>
                <div className="text-xs text-blue-600 mt-1">Click to view full analytics data being sent to AI</div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl p-4 rounded-lg ${
                message.type === 'user'
                  ? 'bg-instagram-purple text-white'
                  : message.isError
                  ? 'bg-red-50 border border-red-200 text-red-800'
                  : 'bg-white shadow-sm border border-gray-200'
              }`}
            >
              {message.type === 'assistant' && (
                <div className="flex items-center mb-2">
                  <Bot className="w-4 h-4 mr-2 text-instagram-purple" />
                  <span className="text-sm font-medium text-gray-600">Assistant</span>
                </div>
              )}
              
              <div
                className={`prose prose-sm max-w-none ${
                  message.type === 'user' ? 'prose-invert' : ''
                }`}
                dangerouslySetInnerHTML={{
                  __html: formatMessage(message.content)
                }}
              />
              
              {message.analytics_summary && (
                <div 
                  className="mt-3 p-3 bg-blue-50 rounded-md border border-blue-200 cursor-pointer hover:bg-blue-100 transition-colors duration-200"
                  onClick={() => handleAnalyticsContextClick(message.analytics_summary)}
                  title="Click to view detailed analytics context"
                >
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-medium text-blue-800 mb-1">📊 Analytics Context</div>
                    <div className="text-blue-600 hover:text-blue-800">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </div>
                  </div>
                  <div className="text-xs text-blue-700 space-y-1">
                    <div>Period: {message.analytics_summary.period_days} days</div>
                    <div>Posts: {message.analytics_summary.total_posts}</div>
                    <div>Engagement: {message.analytics_summary.total_engagement}</div>
                  </div>
                </div>
              )}
              
              <div className="text-xs text-gray-400 mt-2">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white shadow-sm border border-gray-200 p-4 rounded-lg">
              <div className="flex items-center space-x-2">
                <Bot className="w-4 h-4 text-instagram-purple" />
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-instagram-purple rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-instagram-purple rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-instagram-purple rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions */}
      {messages.length <= 1 && (
        <div className="px-4 py-2 bg-white border-t">
          <div className="text-sm text-gray-600 mb-2">💡 Try asking:</div>
          <div className="flex flex-wrap gap-2">
            {getSuggestedQuestions().slice(0, 3).map((question, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(question)}
                className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="bg-white border-t p-4">
        <div className="flex space-x-3">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your Instagram analytics..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-instagram-purple focus:border-transparent resize-none"
              rows="1"
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-6 py-3 bg-instagram-purple text-white rounded-lg hover:bg-instagram-pink focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-instagram-purple disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        <div className="mt-2 text-xs text-gray-500 flex items-center justify-between">
          <span>Press Enter to send • Shift+Enter for new line</span>
          <span>Session: {sessionId.split('_')[1]}</span>
        </div>
      </div>

      {/* Analytics Context Dialog */}
      {showAnalyticsDialog && selectedAnalyticsData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-lg font-semibold text-gray-900">📊 Analytics Context Data</h2>
              <button
                onClick={() => setShowAnalyticsDialog(false)}
                className="text-gray-400 hover:text-gray-600 focus:outline-none"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-4 overflow-y-auto max-h-[calc(80vh-120px)]">
              <div className="space-y-6">
                {/* Summary */}
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="text-sm font-semibold text-blue-900 mb-3">📈 Summary</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-blue-700 font-medium">Period:</span>
                      <div className="text-blue-900">{selectedAnalyticsData.period_days || selectedAnalyticsData.summary?.period_days || 'N/A'} days</div>
                    </div>
                    <div>
                      <span className="text-blue-700 font-medium">Total Posts:</span>
                      <div className="text-blue-900">{selectedAnalyticsData.total_posts || selectedAnalyticsData.summary?.total_posts || 0}</div>
                    </div>
                    <div>
                      <span className="text-blue-700 font-medium">Total Engagement:</span>
                      <div className="text-blue-900">{(selectedAnalyticsData.total_engagement || selectedAnalyticsData.summary?.total_engagement || 0).toLocaleString()}</div>
                    </div>
                    <div>
                      <span className="text-blue-700 font-medium">Accounts:</span>
                      <div className="text-blue-900">{selectedAnalyticsData.total_profiles || selectedAnalyticsData.summary?.total_profiles || selectedAnalyticsData.user_profiles?.length || 0}</div>
                    </div>
                  </div>
                </div>

                {/* Detailed Analytics in Markdown Format */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">� Detailed Analytics Data</h3>
                  <div className="bg-white p-4 rounded border max-h-96 overflow-y-auto">
                    <ReactMarkdown 
                      components={{
                        h1: ({children}) => <h1 className="text-lg font-bold text-gray-900 mt-4 mb-2">{children}</h1>,
                        h2: ({children}) => <h2 className="text-base font-semibold text-gray-800 mt-3 mb-2">{children}</h2>,
                        h3: ({children}) => <h3 className="text-sm font-medium text-gray-700 mt-2 mb-1">{children}</h3>,
                        ul: ({children}) => <ul className="list-disc list-inside text-sm text-gray-600 mb-2">{children}</ul>,
                        li: ({children}) => <li className="mb-1">{children}</li>,
                        table: ({children}) => <table className="table-auto border-collapse border border-gray-300 text-xs w-full mb-3">{children}</table>,
                        th: ({children}) => <th className="border border-gray-300 px-2 py-1 bg-gray-100 font-medium">{children}</th>,
                        td: ({children}) => <td className="border border-gray-300 px-2 py-1">{children}</td>,
                        code: ({children}) => <code className="bg-gray-100 px-1 py-0.5 rounded text-xs">{children}</code>,
                        pre: ({children}) => <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto mb-2">{children}</pre>,
                        p: ({children}) => <p className="text-sm text-gray-700 mb-2">{children}</p>,
                        strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
                        em: ({children}) => <em className="italic text-gray-700">{children}</em>
                      }}
                    >
                      {convertToMarkdown(selectedAnalyticsData)}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="border-t p-4 bg-gray-50">
              <p className="text-xs text-gray-600">
                💡 This is the data context that gets sent to the AI assistant to help it provide relevant insights about your Instagram analytics.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
