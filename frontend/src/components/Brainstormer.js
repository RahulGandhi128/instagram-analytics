import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Lightbulb, 
  Brain,
  RefreshCw,
  Clock,
  User,
  Bot,
  TrendingUp,
  Calendar,
  Hash,
  Users,
  MessageCircle,
  Sparkles
} from 'lucide-react';

const Brainstormer = ({ analyticsData, selectedUsername, timeRange, showNotification }) => {
  const [sessionId] = useState(() => `brainstorm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize brainstormer with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage = {
        id: `msg_${Date.now()}`,
        type: 'assistant',
        content: `👋 Hi! I'm your Brainstormer AI. I analyze your analytics data to suggest content ideas, optimal posting times, and trending topics.\n\n${
          analyticsData 
            ? `I can see you have analytics data for ${selectedUsername || 'your account'}. Ask me for content ideas, posting strategies, or trend analysis!`
            : 'Select an account in the Analytics Context above, and I\'ll help you brainstorm content ideas based on your performance data.'
        }`,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [analyticsData, selectedUsername]);

  const generateBrainstormResponse = async (userMessage) => {
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/brainstormer/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
          analytics_data: analyticsData,
          username: selectedUsername,
          time_range: timeRange
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      return {
        id: `msg_${Date.now()}`,
        type: 'assistant',
        content: data.response,
        timestamp: new Date(),
        suggestions: data.suggestions || []
      };
    } catch (error) {
      console.error('Error generating brainstorm response:', error);
      showNotification?.('Failed to generate brainstorm response. Please try again.', 'error');
      
      return {
        id: `msg_${Date.now()}`,
        type: 'assistant',
        content: `Sorry, I encountered an error while analyzing your data. Please try asking again or check if your analytics data is properly loaded.`,
        timestamp: new Date(),
        isError: true
      };
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!currentInput.trim() || isLoading) return;

    const userMessage = {
      id: `msg_${Date.now()}`,
      type: 'user',
      content: currentInput.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentInput('');

    const assistantResponse = await generateBrainstormResponse(userMessage.content);
    setMessages(prev => [...prev, assistantResponse]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickSuggestions = [
    "What content should I post this week?",
    "When are the best times to post?",
    "What hashtags are performing well?",
    "Suggest trending topics for my niche",
    "Analyze my top performing content",
    "What content types get the most engagement?"
  ];

  const handleQuickSuggestion = (suggestion) => {
    setCurrentInput(suggestion);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="bg-gradient-to-r from-purple-500 to-blue-500 text-white p-2 rounded-lg">
          <Brain className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">🧠 Brainstormer AI</h3>
          <p className="text-sm text-gray-600">
            Content ideation and strategy suggestions based on your analytics
          </p>
        </div>
      </div>

      {/* Analytics Status */}
      {analyticsData ? (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2 text-green-800">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm font-medium">
              Analytics Loaded: {selectedUsername} ({timeRange} days)
            </span>
          </div>
          <div className="text-xs text-green-700 mt-1">
            {analyticsData.analytics?.basic_stats?.total_content || 0} posts • 
            {(analyticsData.analytics?.basic_stats?.total_engagement || 0).toLocaleString()} total engagement
          </div>
        </div>
      ) : (
        <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
          <div className="flex items-center gap-2 text-orange-800">
            <MessageCircle className="w-4 h-4" />
            <span className="text-sm font-medium">
              Select an account above to get personalized brainstorming
            </span>
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div className="mb-4 h-80 overflow-y-auto border border-purple-200 rounded-lg p-4 bg-white">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`mb-4 flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[80%] ${message.type === 'user' ? 'order-2' : ''}`}>
              <div
                className={`p-3 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-purple-500 text-white'
                    : message.isError
                    ? 'bg-red-50 text-red-800 border border-red-200'
                    : 'bg-gray-50 text-gray-800 border border-gray-200'
                }`}
              >
                <div className="whitespace-pre-wrap text-sm">
                  {message.content}
                </div>
                
                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <div className="text-xs font-medium text-gray-600">💡 Quick Ideas:</div>
                    {message.suggestions.map((suggestion, index) => (
                      <div key={index} className="text-xs bg-blue-50 border border-blue-200 p-2 rounded">
                        {suggestion}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className={`text-xs text-gray-500 mt-1 ${
                message.type === 'user' ? 'text-right' : 'text-left'
              }`}>
                <div className="flex items-center gap-1">
                  {message.type === 'user' ? (
                    <User className="w-3 h-3" />
                  ) : (
                    <Brain className="w-3 h-3" />
                  )}
                  <span>{formatTimestamp(message.timestamp)}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-50 border border-gray-200 p-3 rounded-lg">
              <div className="flex items-center gap-2 text-gray-600">
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span className="text-sm">Brainstorming ideas...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Suggestions */}
      {messages.length <= 1 && (
        <div className="mb-4">
          <div className="text-sm font-medium text-gray-700 mb-2">💡 Try asking:</div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {quickSuggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleQuickSuggestion(suggestion)}
                className="text-left text-xs p-2 bg-white border border-purple-200 hover:border-purple-300 rounded-lg hover:bg-purple-50 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <textarea
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me for content ideas, posting strategies, or trend analysis..."
            className="w-full px-3 py-2 border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
            rows="2"
            disabled={isLoading}
          />
        </div>
        <button
          onClick={handleSendMessage}
          disabled={!currentInput.trim() || isLoading}
          className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default Brainstormer;
