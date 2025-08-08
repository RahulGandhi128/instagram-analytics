import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Image, 
  Video, 
  FileText, 
  Palette,
  Bot,
  Download,
  Copy,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  User,
  Sparkles,
  Settings,
  BarChart3,
  Eye,
  X
} from 'lucide-react';
import { useUsernames } from '../hooks/useUsernames';

const ContentCreator = ({ analyticsContext, showNotification }) => {
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [contentType, setContentType] = useState('text');
  const [stylePreferences, setStylePreferences] = useState({
    style: '',
    colors: '',
    mood: 'professional'
  });
  const [conversationHistory, setConversationHistory] = useState([]);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [showAnalyticsModal, setShowAnalyticsModal] = useState(false);
  const [timeRange, setTimeRange] = useState(30);
  const [selectedUsername, setSelectedUsername] = useState('');
  const [downloadingImages, setDownloadingImages] = useState(new Set());
  const messagesEndRef = useRef(null);
  
  // Get usernames for the dropdown
  const { usernames: allUsernames } = useUsernames();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load conversation history when component mounts
    loadConversationHistory();
  }, [sessionId]);

  useEffect(() => {
    // Load analytics data when username or time range changes
    if (selectedUsername) {
      loadAnalyticsData();
    } else {
      setAnalyticsData(null);
    }
  }, [selectedUsername, timeRange]);

  const loadAnalyticsData = async () => {
    if (!selectedUsername) return;
    
    setAnalyticsLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/content/analytics-context/${selectedUsername}`);
      const data = await response.json();
      
      if (data.success) {
        setAnalyticsData(data.context);
        if (showNotification) {
          showNotification('Analytics context loaded successfully', 'success');
        }
      } else {
        console.error('Failed to load analytics data:', data.error);
        setAnalyticsData(null);
        if (showNotification) {
          showNotification('Failed to load analytics data', 'error');
        }
      }
    } catch (error) {
      console.error('Error loading analytics data:', error);
      setAnalyticsData(null);
      if (showNotification) {
        showNotification('Error loading analytics data', 'error');
      }
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const loadConversationHistory = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/content/conversation/${sessionId}`);
      const data = await response.json();
      
      if (data.history && data.history.length > 0) {
        setConversationHistory(data.history);
        setMessages(data.history.map(msg => ({
          id: Date.now() + Math.random(),
          type: msg.role === 'user' ? 'user' : 'assistant',
          content: msg.content,
          timestamp: new Date(msg.timestamp || Date.now()),
          metadata: msg.metadata
        })));
      }
    } catch (error) {
      console.error('Error loading conversation history:', error);
    }
  };

  const getAnalyticsContext = async () => {
    // Use already loaded analytics data if available
    if (analyticsData) {
      return analyticsData;
    }
    
    if (!selectedUsername) return null;
    
    try {
      const response = await fetch(`http://localhost:5000/api/content/analytics-context/${selectedUsername}`);
      const data = await response.json();
      
      if (data.success) {
        setAnalyticsData(data.context);
        return data.context;
      }
      return null;
    } catch (error) {
      console.error('Error fetching analytics context:', error);
      return null;
    }
  };

  const createContent = async () => {
    if (!currentInput.trim()) return;

    setIsLoading(true);
    
    // Add user message to UI immediately
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: currentInput,
      timestamp: new Date(),
      contentType
    };
    
    setMessages(prev => [...prev, userMessage]);
    const prompt = currentInput;
    setCurrentInput('');

    try {
      // Get fresh analytics context
      const context = await getAnalyticsContext();
      
      const requestData = {
        user_id: selectedUsername || 'anonymous',
        prompt: prompt,
        content_type: contentType,
        analytics_context: context || analyticsContext,
        style_preferences: stylePreferences,
        session_id: sessionId
      };

      const response = await fetch('http://localhost:5000/api/content/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      const result = await response.json();
      
      // Add assistant response to UI
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: result.description || result.error || 'Content generated',
        timestamp: new Date(),
        contentType: result.content_type,
        contentUrl: result.content_url,
        contentData: result.content_data,
        metadata: result.metadata,
        error: result.error,
        debugInfo: result.debug_info
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (error) {
      console.error('Error creating content:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `Error: ${error.message}`,
        timestamp: new Date(),
        error: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      if (showNotification) {
        showNotification('Copied to clipboard', 'success');
      }
    }).catch((error) => {
      console.error('Failed to copy:', error);
      if (showNotification) {
        showNotification('Failed to copy to clipboard', 'error');
      }
    });
  };

  const viewImageFullscreen = (url) => {
    // Open image in new tab without affecting current state
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const downloadImage = async (url, filename, messageId) => {
    setDownloadingImages(prev => new Set([...prev, messageId]));
    
    try {
      // Fetch the image as blob to download directly
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error('Failed to fetch image');
      }
      
      const blob = await response.blob();
      
      // Create download link
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      
      if (showNotification) {
        showNotification('Image downloaded successfully', 'success');
      }
    } catch (error) {
      console.error('Error downloading image:', error);
      if (showNotification) {
        showNotification('Failed to download image', 'error');
      }
    } finally {
      setDownloadingImages(prev => {
        const newSet = new Set(prev);
        newSet.delete(messageId);
        return newSet;
      });
    }
  };

  const renderMessage = (message) => {
    if (message.type === 'user') {
      return (
        <div key={message.id} className="flex justify-end mb-4">
          <div className="bg-blue-500 text-white rounded-lg px-4 py-2 max-w-xs lg:max-w-md">
            <div className="flex items-center gap-2 mb-1">
              <User className="w-4 h-4" />
              <span className="text-xs opacity-75">You</span>
              {message.contentType && (
                <span className="text-xs bg-blue-600 px-2 py-0.5 rounded">
                  {message.contentType}
                </span>
              )}
            </div>
            <p className="text-sm">{message.content}</p>
            <p className="text-xs opacity-75 mt-1">
              {message.timestamp.toLocaleTimeString()}
            </p>
          </div>
        </div>
      );
    }

    return (
      <div key={message.id} className="flex justify-start mb-4">
        <div className={`rounded-lg px-4 py-2 max-w-xs lg:max-w-md ${
          message.error ? 'bg-red-100 border border-red-300' : 'bg-gray-100'
        }`}>
          <div className="flex items-center gap-2 mb-2">
            <Bot className="w-4 h-4 text-purple-500" />
            <span className="text-xs font-medium text-gray-600">AI Assistant</span>
            {message.contentType && (
              <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
                {message.contentType}
              </span>
            )}
            {message.error && (
              <AlertCircle className="w-4 h-4 text-red-500" />
            )}
          </div>
          
          {/* Content */}
          <div className="text-sm text-gray-800 mb-2">
            {message.content.split('\n').map((line, index) => (
              <p key={index} className="mb-1">{line}</p>
            ))}
          </div>
          
          {/* Generated Image */}
          {message.contentUrl && message.contentType === 'image' && (
            <div className="mb-3">
              <div className="relative group">
                <img 
                  src={message.contentUrl} 
                  alt="Generated content" 
                  className="max-w-full h-auto rounded-lg border cursor-pointer hover:opacity-90 transition-opacity"
                  onClick={() => viewImageFullscreen(message.contentUrl)}
                  title="Click to view fullscreen"
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-200 rounded-lg flex items-center justify-center">
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-white bg-opacity-90 rounded-full p-2">
                    <Eye className="w-5 h-5 text-gray-700" />
                  </div>
                </div>
              </div>
              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => viewImageFullscreen(message.contentUrl)}
                  className="flex-1 text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-2 rounded-lg flex items-center justify-center gap-1 transition-colors border border-blue-200"
                >
                  <Eye className="w-3 h-3" />
                  View Fullscreen
                </button>
                <button
                  onClick={() => downloadImage(message.contentUrl, `ai-generated-${Date.now()}.png`, message.id)}
                  disabled={downloadingImages.has(message.id)}
                  className="flex-1 text-xs bg-purple-50 hover:bg-purple-100 disabled:bg-gray-100 text-purple-700 disabled:text-gray-500 px-3 py-2 rounded-lg flex items-center justify-center gap-1 transition-colors border border-purple-200 disabled:border-gray-300"
                >
                  {downloadingImages.has(message.id) ? (
                    <>
                      <RefreshCw className="w-3 h-3 animate-spin" />
                      Downloading...
                    </>
                  ) : (
                    <>
                      <Download className="w-3 h-3" />
                      Download
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
          
          {/* Debug Info */}
          {message.debugInfo && (
            <div className="text-xs bg-yellow-50 border border-yellow-200 rounded p-2 mb-2">
              <p className="font-medium text-yellow-800 mb-1">Debug Info:</p>
              <pre className="text-yellow-700 overflow-x-auto">
                {JSON.stringify(message.debugInfo, null, 2)}
              </pre>
            </div>
          )}
          
          {/* Actions */}
          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-500">
              {message.timestamp.toLocaleTimeString()}
            </p>
            <div className="flex items-center gap-2">
              {message.contentUrl && (
                <button
                  onClick={() => copyToClipboard(message.contentUrl)}
                  className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 transition-colors"
                >
                  <Copy className="w-3 h-3" />
                  Copy URL
                </button>
              )}
              <button
                onClick={() => copyToClipboard(message.content)}
                className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 transition-colors"
              >
                <Copy className="w-3 h-3" />
                Copy Text
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const contentTypeOptions = [
    { value: 'text', label: 'Text Content', icon: FileText },
    { value: 'image', label: 'Image/Visual', icon: Image },
    { value: 'graphic', label: 'Graphic Design', icon: Palette },
    { value: 'video', label: 'Video Concept', icon: Video }
  ];

  const styleOptions = [
    'minimalist', 'vibrant', 'elegant', 'playful', 'professional', 
    'artistic', 'modern', 'vintage', 'bold', 'soft'
  ];

  const colorPalettes = [
    'warm tones', 'cool tones', 'monochrome', 'bright colors', 
    'pastel colors', 'earth tones', 'neon colors', 'natural colors'
  ];

  const moodOptions = [
    'professional', 'casual', 'energetic', 'calm', 'inspiring', 
    'fun', 'serious', 'creative', 'motivational', 'friendly'
  ];

  return (
    <div className="space-y-6">
      {/* Analytics Context Card */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-blue-900">Analytics Context</h3>
          </div>
          <button
            onClick={() => setShowAnalyticsModal(true)}
            className="flex items-center gap-1 px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg text-sm transition-colors"
          >
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-blue-700 mb-1">Account Filter</label>
            <select
              value={selectedUsername}
              onChange={(e) => setSelectedUsername(e.target.value)}
              className="w-full text-sm border border-blue-200 rounded px-3 py-2 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Accounts</option>
              {allUsernames.map(username => (
                <option key={username} value={username}>{username}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-blue-700 mb-1">Time Period</label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(parseInt(e.target.value))}
              className="w-full text-sm border border-blue-200 rounded px-3 py-2 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
        </div>

        <div className="mt-3 p-3 bg-white border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium text-blue-800">
                📊 Context: {analyticsLoading ? 'Loading...' : (
                  analyticsData ? 
                    `${analyticsData.analytics?.basic_stats?.total_content || 0} posts, ${(analyticsData.analytics?.basic_stats?.total_engagement || 0).toLocaleString()} total engagement` :
                    selectedUsername ? 'No data available' : '0 posts, 0 total engagement'
                )}
              </span>
            </div>
            <button
              onClick={() => setShowAnalyticsModal(true)}
              className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 transition-colors"
            >
              <Eye className="w-3 h-3" />
              View details
            </button>
          </div>
          {analyticsData && (
            <p className="text-xs text-blue-600 mt-1">
              ✅ AI will use {selectedUsername}'s performance data to personalize content suggestions
            </p>
          )}
          {!selectedUsername && (
            <p className="text-xs text-orange-600 mt-1">
              ⚠️ Select an account above for personalized content suggestions
            </p>
          )}
        </div>
      </div>

      {/* Analytics Modal */}
      {showAnalyticsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Analytics Data Being Sent to AI</h3>
              <button
                onClick={() => setShowAnalyticsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4">
              {analyticsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
                  <span className="ml-2 text-gray-600">Loading analytics data...</span>
                </div>
              ) : analyticsData ? (
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="font-medium text-green-800 mb-2">📊 Analytics Summary</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-green-600 font-medium">Total Content</p>
                        <p className="text-green-800">{analyticsData.analytics?.basic_stats?.total_content || 0} posts</p>
                      </div>
                      <div>
                        <p className="text-green-600 font-medium">Total Engagement</p>
                        <p className="text-green-800">{(analyticsData.analytics?.basic_stats?.total_engagement || 0).toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-green-600 font-medium">Avg Engagement</p>
                        <p className="text-green-800">{Math.round(analyticsData.analytics?.basic_stats?.avg_engagement_per_post || 0)}</p>
                      </div>
                    </div>
                  </div>

                  {analyticsData.insights?.top_posts?.length > 0 && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h4 className="font-medium text-blue-800 mb-2">🏆 Top Performing Content</h4>
                      <div className="space-y-2">
                        {analyticsData.insights.top_posts.slice(0, 3).map((post, index) => (
                          <div key={index} className="text-sm bg-white p-2 rounded border">
                            <p className="font-medium">{post.media_type} - {post.engagement} engagement</p>
                            {post.hashtags && post.hashtags.length > 0 && (
                              <p className="text-blue-600">{post.hashtags.join(' ')}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-800 mb-2">🔍 Raw Data Preview</h4>
                    <pre className="text-xs bg-white p-3 rounded border overflow-x-auto">
                      {JSON.stringify(analyticsData, null, 2)}
                    </pre>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No analytics data available</p>
                  <p className="text-sm mt-1">Select an account to load analytics context</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* AI Content Creator */}
      <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-2 rounded-lg">
          <Sparkles className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">AI Content Creator</h3>
          <p className="text-sm text-gray-600">
            Generate engaging content with AI assistance and analytics insights
          </p>
        </div>
      </div>

      {/* Content Type Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Content Type
        </label>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
          {contentTypeOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setContentType(option.value)}
              className={`p-3 rounded-lg border text-sm font-medium transition-colors ${
                contentType === option.value
                  ? 'bg-purple-100 border-purple-300 text-purple-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <option.icon className="w-4 h-4 mx-auto mb-1" />
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Style Preferences */}
      {(contentType === 'image' || contentType === 'graphic') && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Style Preferences</h4>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Style</label>
              <select
                value={stylePreferences.style}
                onChange={(e) => setStylePreferences(prev => ({ ...prev, style: e.target.value }))}
                className="w-full text-xs border border-gray-300 rounded px-2 py-1"
              >
                <option value="">Select style...</option>
                {styleOptions.map(style => (
                  <option key={style} value={style}>{style}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Colors</label>
              <select
                value={stylePreferences.colors}
                onChange={(e) => setStylePreferences(prev => ({ ...prev, colors: e.target.value }))}
                className="w-full text-xs border border-gray-300 rounded px-2 py-1"
              >
                <option value="">Select colors...</option>
                {colorPalettes.map(palette => (
                  <option key={palette} value={palette}>{palette}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Mood</label>
              <select
                value={stylePreferences.mood}
                onChange={(e) => setStylePreferences(prev => ({ ...prev, mood: e.target.value }))}
                className="w-full text-xs border border-gray-300 rounded px-2 py-1"
              >
                {moodOptions.map(mood => (
                  <option key={mood} value={mood}>{mood}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Analytics Context Info */}
      {selectedUsername && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle className="w-4 h-4 text-blue-500" />
            <span className="text-sm font-medium text-blue-800">Analytics Context Active</span>
          </div>
          <p className="text-xs text-blue-700">
            Content suggestions will be personalized based on {selectedUsername}'s performance data and audience insights.
          </p>
        </div>
      )}

      {/* Chat Messages */}
      <div className="mb-4 h-96 overflow-y-auto border border-gray-200 rounded-lg p-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Bot className="w-12 h-12 mb-2 opacity-50" />
            <p className="text-sm text-center">
              Start creating content! Ask me to generate images, write captions, or create video concepts.
            </p>
            <div className="mt-4 text-xs space-y-1">
              <p>Try asking:</p>
              <p className="bg-gray-100 px-2 py-1 rounded">"Create a motivational Instagram post"</p>
              <p className="bg-gray-100 px-2 py-1 rounded">"Design a graphic for my latest product"</p>
              <p className="bg-gray-100 px-2 py-1 rounded">"Write a caption for a food photo"</p>
            </div>
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-purple-500" />
                <span className="text-sm text-gray-600">Creating content...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex gap-2">
        <input
          type="text"
          value={currentInput}
          onChange={(e) => setCurrentInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !isLoading && createContent()}
          placeholder={`Ask me to create ${contentType} content...`}
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          disabled={isLoading}
        />
        <button
          onClick={createContent}
          disabled={isLoading || !currentInput.trim()}
          className="bg-purple-500 hover:bg-purple-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
        >
          {isLoading ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
          Create
        </button>
      </div>

      {/* Quick Actions */}
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          onClick={() => setCurrentInput('Create an engaging Instagram story graphic')}
          className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full"
        >
          Story Graphic
        </button>
        <button
          onClick={() => setCurrentInput('Write a catchy caption with hashtags')}
          className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full"
        >
          Caption + Hashtags
        </button>
        <button
          onClick={() => setCurrentInput('Design a promotional post for my brand')}
          className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full"
        >
          Promotional Post
        </button>
        <button
          onClick={() => setCurrentInput('Create a video concept for higher engagement')}
          className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full"
        >
          Video Concept
        </button>
      </div>
      </div>
    </div>
  );
};

export default ContentCreator;
