import React, { useState, useEffect, useCallback } from 'react';
import { Users, MessageCircle, Heart, TrendingUp, BarChart, Download, Info } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart as RechartsBarChart, Bar, ComposedChart, PieChart, Pie, Cell } from 'recharts';
import { analyticsAPI } from '../services/api';
import { useUsernames } from '../hooks/useUsernames';
import { useNavigate } from 'react-router-dom';

const Dashboard = ({ showNotification }) => {
  const navigate = useNavigate();
  const [summaryStats, setSummaryStats] = useState(null);
  const [dailyMetrics, setDailyMetrics] = useState([]);
  const [insights, setInsights] = useState({});
  const [selectedUsername, setSelectedUsername] = useState('');
  const [loading, setLoading] = useState(true);
  const [chartTimeRange, setChartTimeRange] = useState(30);
  const [lastFetchTime, setLastFetchTime] = useState(null);
  const [fetchingData, setFetchingData] = useState(false);
  const [hashtagData, setHashtagData] = useState([]);
  const [cumulativeHashtagData, setCumulativeHashtagData] = useState([]);
  const [mediaPostsData, setMediaPostsData] = useState([]);
  const [comprehensiveAnalytics, setComprehensiveAnalytics] = useState(null);
  
  const { usernames: allUsernames } = useUsernames();

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const params = { days: chartTimeRange };
      if (selectedUsername) params.username = selectedUsername;

      // Use centralized analytics service for all data
      const [summaryRes, mediaRes, insightsRes, dailyChartRes, comprehensiveRes] = await Promise.all([
        analyticsAPI.getSummaryStats(params),
        analyticsAPI.getMedia(params),
        analyticsAPI.getInsights(params),
        // New: Get daily chart data from analytics service
        fetch(`http://localhost:5000/api/analytics/daily-chart?${new URLSearchParams(params)}`).then(r => r.json()),
        // New: Get comprehensive analytics data
        fetch(`http://localhost:5000/api/analytics/comprehensive?${new URLSearchParams(params)}`).then(r => r.json())
      ]);

      setSummaryStats(summaryRes.data.data);
      
      // Store media posts data for compatibility (minimal usage now)
      const mediaData = mediaRes.data.data || [];
      setMediaPostsData(mediaData);
      
      // Use analytics service data instead of local calculations
      if (dailyChartRes.success) {
        setDailyMetrics(dailyChartRes.data);
      }
      
      // Extract hashtag data from comprehensive analytics
      if (comprehensiveRes.success && comprehensiveRes.data.hashtags) {
        const hashtagAnalytics = comprehensiveRes.data.hashtags;
        // Use trending_hashtags which has proper structure for charts
        const trendingData = hashtagAnalytics.trending_hashtags || [];
        setHashtagData(trendingData.map(tag => ({
          hashtag: tag.hashtag.replace('#', ''),
          posts: tag.total_posts,
          totalEngagement: tag.total_engagement,
          avgEngagement: Math.round(tag.avg_engagement),
          engagement_display: tag.engagement_display
        })));
        setCumulativeHashtagData(hashtagAnalytics.top_hashtags || []);
      }
      
      // Store comprehensive analytics for performance metrics
      if (comprehensiveRes.success) {
        setComprehensiveAnalytics(comprehensiveRes.data);
      }
      
      setInsights(insightsRes.data.data);
      
      // Debug logging for analytics service data
      console.log('Dashboard Data Updated (Centralized):', {
        selectedUsername,
        chartTimeRange,
        dailyMetricsCount: dailyChartRes.data?.length || 0,
        hashtagCount: comprehensiveRes.data?.hashtags?.trending_hashtags?.length || 0,
        comprehensiveData: comprehensiveRes.data?.metadata
      });
    } catch (error) {
      console.error('Error loading centralized dashboard data:', error);
      showNotification('Error loading dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  }, [chartTimeRange, selectedUsername, showNotification]);

  // Remove local calculations - now using centralized analytics service
  // All data processing is handled by the backend analytics service

  useEffect(() => {
    fetchDashboardData();
    // Check if there's a stored last fetch time
    const storedFetchTime = localStorage.getItem('lastFetchTime');
    if (storedFetchTime) {
      setLastFetchTime(new Date(storedFetchTime));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  // Separate effect for when filters change
  useEffect(() => {
    fetchDashboardData();
  }, [selectedUsername, chartTimeRange, fetchDashboardData]);

  const fetchInstagramData = async () => {
    setFetchingData(true);
    try {
      showNotification('Fetching latest Instagram data... This may take a few minutes', 'info');
      const response = await fetch('http://localhost:5000/api/fetch-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      
      if (data.success) {
        const fetchTime = new Date();
        setLastFetchTime(fetchTime);
        localStorage.setItem('lastFetchTime', fetchTime.toISOString());
        
        // Trigger global refresh event
        window.dispatchEvent(new CustomEvent('dataFetched', { detail: { timestamp: fetchTime } }));
        
        showNotification('Instagram data updated successfully!', 'success');
        await fetchDashboardData(); // Refresh dashboard data
      } else {
        showNotification(`Error: ${data.error}`, 'error');
      }
    } catch (error) {
      showNotification('Error fetching Instagram data', 'error');
    } finally {
      setFetchingData(false);
    }
  };

  const handleUsernameChange = async (username) => {
    setSelectedUsername(username);
    // fetchDashboardData will be triggered by useEffect when selectedUsername changes
  };

  const handleTimeRangeChange = async (timeRange) => {
    setChartTimeRange(timeRange);
    // fetchDashboardData will be triggered by useEffect when chartTimeRange changes
  };

  const exportData = async (type) => {
    try {
      const params = selectedUsername ? { username: selectedUsername, type } : { type };
      const response = await analyticsAPI.exportCSV(params);
      
      // Create and download CSV
      const csvData = response.data.data;
      const csvContent = Object.keys(csvData[0]).join(',') + '\n' + 
        csvData.map(row => Object.values(row).join(',')).join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.data.filename;
      a.click();
      window.URL.revokeObjectURL(url);
      
      showNotification('Data exported successfully!', 'success');
    } catch (error) {
      showNotification('Error exporting data', 'error');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-instagram-purple"></div>
      </div>
    );
  }

  const currentUserInsights = selectedUsername && insights[selectedUsername] ? insights[selectedUsername] : null;

  // Filter insights data by time range if available
  const getFilteredInsights = () => {
    if (!currentUserInsights) return null;
    
    // Filter media posts by the selected time range and get top/bottom performing
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - chartTimeRange);
    
    const filteredPosts = mediaPostsData.filter(post => {
      if (!post.post_datetime_ist) return false;
      const postDate = new Date(post.post_datetime_ist);
      return postDate >= cutoffDate && (!selectedUsername || post.og_username === selectedUsername);
    });
    
    // Sort by engagement and get top/bottom posts
    const sortedByEngagement = filteredPosts
      .map(post => ({
        ...post,
        engagement: (post.like_count || 0) + (post.comment_count || 0),
        likes: post.like_count || 0,
        comments: post.comment_count || 0,
        media_type: post.media_type || 'post',
        post_date: post.post_datetime_ist,
        hashtags: post.caption ? (post.caption.match(/#\w+/g) || []).slice(0, 3) : []
      }))
      .sort((a, b) => b.engagement - a.engagement);
    
    const topPosts = sortedByEngagement.slice(0, 5);
    const bottomPosts = sortedByEngagement.slice(-5).reverse();

    return {
      ...currentUserInsights,
      top_posts: topPosts,
      bottom_posts: bottomPosts
    };
  };

  // Generate filtered summary stats based on selected filters
  const getFilteredSummaryStats = () => {
    if (!summaryStats || !mediaPostsData) return summaryStats;
    
    // Calculate filtered stats from media posts data
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - chartTimeRange);
    
    let filteredPosts = mediaPostsData.filter(post => {
      if (!post.post_datetime_ist) return false;
      const postDate = new Date(post.post_datetime_ist);
      const isInTimeRange = postDate >= cutoffDate;
      const isMatchingUser = !selectedUsername || post.og_username === selectedUsername;
      return isInTimeRange && isMatchingUser;
    });
    
    // Get unique profiles from filtered posts
    const uniqueProfiles = [...new Set(filteredPosts.map(post => post.og_username))].length;
    
    // Count active stories (stories posted within the time range)
    const activeStories = filteredPosts.filter(post => post.media_type === 'story').length;
    
    // Calculate posts this week (last 7 days)
    const weekCutoff = new Date();
    weekCutoff.setDate(weekCutoff.getDate() - 7);
    const postsThisWeek = filteredPosts.filter(post => {
      if (!post.post_datetime_ist) return false;
      return new Date(post.post_datetime_ist) >= weekCutoff;
    }).length;
    
    return {
      total_profiles: uniqueProfiles || 0,
      total_posts: filteredPosts.length || 0,
      active_stories: activeStories || 0,
      recent_posts_week: postsThisWeek || 0
    };
  };

  const filteredInsights = getFilteredInsights();
  const filteredSummaryStats = getFilteredSummaryStats();

  const processedDailyMetrics = dailyMetrics.map(metric => {
    const date = new Date(metric.date);
    let dateLabel;
    
    // Format date label based on time range
    if (chartTimeRange <= 7) {
      // For 7 days or less, show day name + date
      dateLabel = date.toLocaleDateString('en-US', { 
        weekday: 'short',
        month: 'numeric',
        day: 'numeric'
      });
    } else if (chartTimeRange <= 30) {
      // For up to 30 days, show month + day
      dateLabel = date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric'
      });
    } else {
      // For longer periods, show month/day
      dateLabel = date.toLocaleDateString('en-US', { 
        month: 'numeric', 
        day: 'numeric'
      });
    }
    
    return {
      ...metric,
      date: dateLabel,
      originalDate: metric.date
    };
  });

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Instagram Data Workflow Bar */}
      <div className="mb-8 bg-gradient-to-r from-instagram-purple to-instagram-pink rounded-lg p-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold mb-2">Instagram Data Workflow</h3>
            <p className="text-sm opacity-90">
              Follow these steps: 1️⃣ Fetch latest Instagram data → 2️⃣ View analytics & insights → 3️⃣ Export reports
            </p>
            <p className="text-xs opacity-75 mt-1">
              • All data synced in IST timezone • Updates profiles, posts, stories & engagement metrics
            </p>
          </div>
          <div className="text-right">
            {lastFetchTime && (
              <div className="text-xs opacity-75 mb-2">
                Last fetched: {lastFetchTime.toLocaleString('en-IN', { 
                  timeZone: 'Asia/Kolkata',
                  year: 'numeric',
                  month: 'short', 
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })} IST
              </div>
            )}
            <button
              onClick={fetchInstagramData}
              disabled={fetchingData}
              className="inline-flex items-center px-6 py-3 bg-white text-instagram-purple font-semibold rounded-lg shadow-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              {fetchingData ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-instagram-purple mr-2"></div>
                  Fetching Data...
                </>
              ) : (
                <>
                  🚀 Fetch Latest Data
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="md:flex md:items-center md:justify-between mb-6">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Dashboard
          </h2>
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4 space-x-3">
          <select
            value={selectedUsername}
            onChange={(e) => handleUsernameChange(e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
          >
            <option value="">All Accounts</option>
            {allUsernames.map(username => (
              <option key={username} value={username}>{username}</option>
            ))}
          </select>
          <select
            value={chartTimeRange}
            onChange={(e) => handleTimeRangeChange(parseInt(e.target.value))}
            className="rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
          >
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button
            onClick={() => exportData('media')}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </button>
          <button
            onClick={() => navigate('/more-info')}
            className="inline-flex items-center px-4 py-2 border border-purple-300 rounded-md shadow-sm text-sm font-medium text-purple-700 bg-purple-50 hover:bg-purple-100"
          >
            <Info className="w-4 h-4 mr-2" />
            More Info
          </button>
        </div>
      </div>

      {/* Debug Info - Remove this in production */}
      <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
        <p><strong>Debug Info:</strong> Selected: "{selectedUsername || 'All'}" | Time: {chartTimeRange} days | Chart Data: {processedDailyMetrics.length} days</p>
        <p><strong>Date Range:</strong> {processedDailyMetrics[0]?.date} to {processedDailyMetrics[processedDailyMetrics.length - 1]?.date}</p>
        <p><strong>Posts Found:</strong> {processedDailyMetrics.reduce((sum, day) => sum + day.posts_count, 0)} total posts | Unique Hashtags: {hashtagData.length} | Total Hashtag Usage: {cumulativeHashtagData.reduce((sum, h) => sum + h.usageCount, 0)}</p>
      </div>

      {/* NEW: Metrics Mentra Overview Dashboard */}
      {filteredInsights && (
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 mb-6">📊 Metrics Mentra - Overview Dashboard</h3>
          
          {/* Primary Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {/* Total Content */}
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm">Total Content</p>
                  <p className="text-2xl font-bold">
                    {filteredInsights.basic_stats?.total_content || filteredInsights.basic_stats?.total_posts || 0}
                  </p>
                  <p className="text-blue-100 text-xs">Post + Carousel + Reels</p>
                </div>
                <BarChart className="h-8 w-8 text-blue-200" />
              </div>
            </div>

            {/* Total Engagement */}
            <div className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm">Total Engagement</p>
                  <p className="text-2xl font-bold">
                    {(filteredInsights.basic_stats?.extended_engagement || filteredInsights.basic_stats?.total_engagement || 0).toLocaleString()}
                  </p>
                  <p className="text-green-100 text-xs">Likes + Comments + Shares</p>
                </div>
                <Heart className="h-8 w-8 text-green-200" />
              </div>
            </div>

            {/* Engagement Per Content */}
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm">Engagement Per Content</p>
                  <p className="text-2xl font-bold">
                    {Math.round(filteredInsights.basic_stats?.engagement_per_content || filteredInsights.basic_stats?.avg_engagement_per_post || 0)}
                  </p>
                  <p className="text-purple-100 text-xs">Average per piece</p>
                </div>
                <TrendingUp className="h-8 w-8 text-purple-200" />
              </div>
            </div>

            {/* Top Performers Count */}
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100 text-sm">Top Performers</p>
                  <p className="text-2xl font-bold">
                    {filteredInsights.top_performers_count || 0}
                  </p>
                  <p className="text-orange-100 text-xs">Above avg engagement</p>
                </div>
                <Users className="h-8 w-8 text-orange-200" />
              </div>
            </div>
          </div>

          {/* Secondary Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
            {/* Total Likes */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="text-center">
                <Heart className="h-6 w-6 text-red-500 mx-auto mb-2" />
                <p className="text-gray-600 text-sm">Total Likes</p>
                <p className="text-xl font-bold text-gray-900">
                  {(filteredInsights.basic_stats?.total_likes || 0).toLocaleString()}
                </p>
              </div>
            </div>

            {/* Total Comments */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="text-center">
                <MessageCircle className="h-6 w-6 text-blue-500 mx-auto mb-2" />
                <p className="text-gray-600 text-sm">Total Comments</p>
                <p className="text-xl font-bold text-gray-900">
                  {(filteredInsights.basic_stats?.total_comments || 0).toLocaleString()}
                </p>
              </div>
            </div>

            {/* Collab Content */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="text-center">
                <Users className="h-6 w-6 text-green-500 mx-auto mb-2" />
                <p className="text-gray-600 text-sm">Collab Content</p>
                <p className="text-xl font-bold text-gray-900">
                  {filteredInsights.basic_stats?.collab_content_count || 0}
                </p>
              </div>
            </div>

            {/* Average Reel Views */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="text-center">
                <TrendingUp className="h-6 w-6 text-purple-500 mx-auto mb-2" />
                <p className="text-gray-600 text-sm">Avg Reel Views</p>
                <p className="text-xl font-bold text-gray-900">
                  {Math.round(filteredInsights.basic_stats?.average_reel_view || 0).toLocaleString()}
                </p>
              </div>
            </div>

            {/* Favoured Content Type */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="text-center">
                <BarChart className="h-6 w-6 text-indigo-500 mx-auto mb-2" />
                <p className="text-gray-600 text-sm">Favoured Mode</p>
                <p className="text-lg font-bold text-gray-900 capitalize">
                  {(() => {
                    // Use comprehensive analytics if available
                    if (comprehensiveAnalytics?.media_types?.best_performing_type && 
                        comprehensiveAnalytics.media_types.best_performing_type !== 'post') {
                      return comprehensiveAnalytics.media_types.best_performing_type;
                    }
                    
                    // Fallback: Calculate from breakdown, excluding 'post'
                    const breakdown = filteredInsights.basic_stats?.content_type_breakdown || {};
                    const validTypes = Object.entries(breakdown).filter(([type, count]) => type !== 'post' && count > 0);
                    
                    if (validTypes.length === 0) return 'N/A';
                    
                    // Find the type with highest count
                    const [bestType] = validTypes.reduce((max, current) => 
                      current[1] > max[1] ? current : max
                    );
                    
                    return bestType;
                  })()}
                </p>
              </div>
            </div>
          </div>

          {/* Content Type Breakdown Chart */}
          {filteredInsights.basic_stats?.content_type_breakdown && (
            <div className="bg-white p-6 rounded-lg shadow mb-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">📊 Content Type Distribution</h4>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Distribution Grid */}
                <div className="grid grid-cols-1 gap-4">
                  {Object.entries(filteredInsights.basic_stats.content_type_breakdown)
                    .filter(([type, count]) => type !== 'post' && count > 0) // Exclude 'post' and zero counts
                    .map(([type, count]) => (
                    <div key={type} className="text-center p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600 capitalize">{type}</p>
                      <p className="text-2xl font-bold text-gray-900">{count}</p>
                      <p className="text-xs text-gray-500">
                        {(filteredInsights.basic_stats.content_engagement_breakdown?.[type] || 0).toLocaleString()} engagement
                      </p>
                    </div>
                  ))}
                </div>

                {/* Pie Chart */}
                <div className="flex flex-col items-center">
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={Object.entries(filteredInsights.basic_stats.content_type_breakdown)
                          .filter(([type, count]) => type !== 'post' && count > 0) // Exclude 'post' and zero counts
                          .map(([type, count]) => ({
                            name: type,
                            value: count,
                            engagement: filteredInsights.basic_stats.content_engagement_breakdown?.[type] || 0
                          }))}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {Object.entries(filteredInsights.basic_stats.content_type_breakdown)
                          .filter(([type, count]) => type !== 'post' && count > 0) // Exclude 'post' and zero counts
                          .map((entry, index) => {
                          const colors = ['#E1306C', '#FF6B35', '#4285F4', '#34A853', '#9C27B0'];
                          return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                        })}
                      </Pie>
                      <Tooltip 
                        formatter={(value, name, props) => [
                          `${value} posts`,
                          `${props.payload.name} (${props.payload.engagement.toLocaleString()} engagement)`
                        ]}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                  <p className="text-xs text-gray-500 text-center mt-2">
                    Content type distribution by post count (Carousel & Reel)
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Missing Data Notice */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <h4 className="text-sm font-medium text-yellow-800 mb-2">📊 Metrics Mentra - Data Availability Status</h4>
            <div className="text-xs text-yellow-700 grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div>
                <p className="font-medium mb-1">✅ Available Metrics:</p>
                <p>• Total Content, Engagement, Likes, Comments</p>
                <p>• Content Type Distribution (Post/Carousel/Reels)</p>
                <p>• Collaboration Content Count</p>
                <p>• Hashtag Performance Analysis</p>
                <p>• Top/Bottom Performers</p>
                <p>• Time Series Engagement Trends</p>
              </div>
              <div>
                <p className="font-medium mb-1">⚠️ Limited Metrics:</p>
                <p>• Reel Views (using available play_count)</p>
                <p>• Shares (using reshare_count)</p>
                <p>• Posting Time Analysis (estimated)</p>
              </div>
              <div>
                <p className="font-medium mb-1">❌ Missing (Requires Business API):</p>
                <p>• Total Reach & Impressions</p>
                <p>• Impression Per Content</p>
                <p>• Detailed Time Analytics</p>
                <p>• Story Metrics</p>
              </div>
            </div>
            <div className="mt-3 p-2 bg-yellow-100 rounded text-center">
              <p className="text-xs text-yellow-800 font-medium">
                💡 To unlock full analytics, upgrade to Instagram Business API access
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Summary Stats Cards */}
      {filteredSummaryStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Users className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {selectedUsername ? `Profile: ${selectedUsername}` : 'Active Profiles'}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {filteredSummaryStats.total_profiles}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Posts ({chartTimeRange} days)
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {filteredSummaryStats.total_posts}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <TrendingUp className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Active Stories ({chartTimeRange} days)
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {filteredSummaryStats.active_stories}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <MessageCircle className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Posts This Week
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {filteredSummaryStats.recent_posts_week}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts - First Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Daily Engagement Trend */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Daily Engagement Trend ({chartTimeRange} days)
          </h3>
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={processedDailyMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                angle={chartTimeRange > 14 ? -45 : 0}
                textAnchor={chartTimeRange > 14 ? 'end' : 'middle'}
                height={chartTimeRange > 14 ? 80 : 60}
                interval="preserveStartEnd"
              />
              <YAxis yAxisId="left" />
              <YAxis 
                yAxisId="right" 
                orientation="right" 
                domain={[0, 'dataMax']}
                tickFormatter={(value) => Math.round(value)}
                allowDecimals={false}
              />
              <Tooltip 
                labelFormatter={(label, payload) => {
                  if (payload && payload[0]) {
                    const data = payload[0].payload;
                    return `${label} (${data.posts_count} posts)`;
                  }
                  return label;
                }}
                formatter={(value, name) => [value, name]}
              />
              <Legend />
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="total_engagement" 
                stroke="#8884d8" 
                strokeWidth={3}
                name="Total Engagement"
                connectNulls={false}
                dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
              />
              <Bar 
                yAxisId="right"
                dataKey="posts_count" 
                fill="rgba(130, 202, 157, 0.8)" 
                name="Posts Count"
                barSize={30}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Posts vs Engagement */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Posts vs Engagement ({chartTimeRange} days)
          </h3>
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={processedDailyMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                angle={chartTimeRange > 14 ? -45 : 0}
                textAnchor={chartTimeRange > 14 ? 'end' : 'middle'}
                height={chartTimeRange > 14 ? 80 : 60}
                interval="preserveStartEnd"
              />
              <YAxis yAxisId="left" />
              <YAxis 
                yAxisId="right" 
                orientation="right" 
                domain={[0, 'dataMax']}
                tickFormatter={(value) => Math.round(value)}
                allowDecimals={false}
              />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'posts_count' ? `${Math.round(value)} posts` : value,
                  name === 'posts_count' ? 'Posts Count' : 'Avg Engagement per Post'
                ]}
              />
              <Legend />
              <Bar 
                yAxisId="right"
                dataKey="posts_count" 
                fill="#8884d8" 
                name="Posts Count" 
                barSize={30}
              />
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="avg_engagement_per_post" 
                stroke="#82ca9d" 
                strokeWidth={3}
                name="Avg Engagement per Post"
                connectNulls={false}
                dot={{ fill: '#82ca9d', strokeWidth: 2, r: 4 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts - Second Row: Trending Hashtag Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* NEW: Trending Hashtags Analysis Table */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            🔥 Trending Hashtags Analysis ({chartTimeRange} days)
          </h3>
          {hashtagData.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Hashtag
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Posts
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Engagement
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avg
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {hashtagData.slice(0, 8).map((hashtag, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-sm font-medium text-instagram-purple">
                            #{hashtag.hashtag}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                        {hashtag.posts} posts
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                        {hashtag.totalEngagement >= 1000 
                          ? `${(hashtag.totalEngagement / 1000).toFixed(1)}k`
                          : hashtag.totalEngagement
                        }
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                        {Math.round(hashtag.avgEngagement)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No hashtag data available</p>
                <p className="text-sm mt-2">Add captions with hashtags to your posts to see trending analysis</p>
              </div>
            </div>
          )}
        </div>

        {/* Hashtag Engagement Distribution (Bar Chart) */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            📊 Hashtag Engagement Distribution ({chartTimeRange} days)
          </h3>
          {hashtagData.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <RechartsBarChart data={hashtagData.slice(0, 6)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="hashtag" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  fontSize={12}
                />
                <YAxis />
                <Tooltip 
                  formatter={(value, name, props) => {
                    // Use dataKey to distinguish between bars
                    if (props.dataKey === 'avgEngagement') {
                      return [`${Math.round(value)} avg`, 'Avg Engagement'];
                    } else if (props.dataKey === 'totalEngagement') {
                      return [`${value}`, 'Total Engagement'];
                    }
                    return [value, name];
                  }}
                  labelFormatter={(label) => {
                    const hashtag = hashtagData.find(h => h.hashtag === label);
                    return `#${label} (${hashtag?.posts || 0} posts)`;
                  }}
                />
                <Legend />
                <Bar dataKey="totalEngagement" fill="#E1306C" name="Total Engagement" />
                <Bar dataKey="avgEngagement" fill="#FF6B35" name="Avg Engagement" />
              </RechartsBarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No hashtag data available</p>
                <p className="text-sm mt-2">Add captions with hashtags to your posts to see distribution</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Charts - Third Row: Time Series Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Engagement Trend Line Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            📈 Engagement Trend (Time Series)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={processedDailyMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                angle={chartTimeRange > 14 ? -45 : 0}
                textAnchor={chartTimeRange > 14 ? 'end' : 'middle'}
                height={chartTimeRange > 14 ? 80 : 60}
                interval="preserveStartEnd"
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(label, payload) => {
                  if (payload && payload[0]) {
                    const data = payload[0].payload;
                    return `${label} (${data.posts_count} posts)`;
                  }
                  return label;
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="total_engagement" 
                stroke="#8884d8" 
                strokeWidth={3}
                name="Total Engagement"
                dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="avg_engagement_per_post" 
                stroke="#82ca9d" 
                strokeWidth={2}
                name="Avg Engagement per Post"
                dot={{ fill: '#82ca9d', strokeWidth: 2, r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Content Type Performance */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            🎯 Content Type Performance
          </h3>
          {(comprehensiveAnalytics?.media_types?.performance_by_type || (filteredInsights && filteredInsights.basic_stats?.content_type_breakdown)) ? (
            <div className="space-y-4">
              {/* Use comprehensive analytics if available, otherwise fall back to filtered insights */}
              {comprehensiveAnalytics?.media_types?.performance_by_type 
                ? Object.entries(comprehensiveAnalytics.media_types.performance_by_type)
                    .filter(([type, stats]) => type !== 'post' && stats.count > 0)
                    .map(([type, stats]) => (
                    <div key={type} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 capitalize">{type}</p>
                        <p className="text-xs text-gray-500">{stats.count} posts • {stats.total_engagement.toLocaleString()} total engagement</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-gray-900">{Math.round(stats.avg_engagement)}</p>
                        <p className="text-xs text-gray-500">avg engagement</p>
                      </div>
                    </div>
                  ))
                : Object.entries(filteredInsights.basic_stats.content_type_breakdown)
                    .filter(([type, count]) => type !== 'post' && count > 0)
                    .map(([type, count]) => {
                    const engagement = filteredInsights.basic_stats.content_engagement_breakdown?.[type] || 0;
                    const avgEngagement = count > 0 ? Math.round(engagement / count) : 0;
                    return (
                      <div key={type} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900 capitalize">{type}</p>
                          <p className="text-xs text-gray-500">{count} posts • {engagement.toLocaleString()} total engagement</p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-gray-900">{avgEngagement}</p>
                          <p className="text-xs text-gray-500">avg engagement</p>
                        </div>
                      </div>
                    );
                  })
              }
              
              {/* Favoured Mode Highlight */}
              <div className="mt-4 p-3 bg-gradient-to-r from-instagram-purple to-instagram-pink text-white rounded-lg">
                <p className="text-sm">🏆 Favoured Mode of Posting</p>
                <p className="text-lg font-bold capitalize">
                  {(() => {
                    // Use comprehensive analytics if available
                    if (comprehensiveAnalytics?.media_types?.best_performing_type && 
                        comprehensiveAnalytics.media_types.best_performing_type !== 'post') {
                      return comprehensiveAnalytics.media_types.best_performing_type;
                    }
                    
                    // Fallback: Calculate from breakdown, excluding 'post'
                    const breakdown = filteredInsights?.basic_stats?.content_type_breakdown || {};
                    const validTypes = Object.entries(breakdown).filter(([type, count]) => type !== 'post' && count > 0);
                    
                    if (validTypes.length === 0) return 'N/A';
                    
                    // Find the type with highest count
                    const [bestType] = validTypes.reduce((max, current) => 
                      current[1] > max[1] ? current : max
                    );
                    
                    return bestType;
                  })()}
                </p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No content type data available</p>
                <p className="text-sm mt-2">Post content to see performance breakdown</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Charts - Fourth Row: Time Analysis and Advanced Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Time of Day Analysis */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            🕐 Favoured Time of Posting Analysis
          </h3>
          {(comprehensiveAnalytics?.posting_times || filteredInsights?.optimal_posting_times) ? (
            <div className="space-y-4">
              {/* Time Period Stats from Analytics Service */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                {comprehensiveAnalytics?.posting_times?.optimal_posting_analysis?.time_period_breakdown ? (
                  <>
                    <div className="text-center p-3 bg-yellow-50 rounded-lg">
                      <p className="text-yellow-600 text-sm">Morning</p>
                      <p className="text-xl font-bold text-yellow-800">
                        {comprehensiveAnalytics.posting_times.optimal_posting_analysis.time_period_breakdown.morning?.percentage || 0}%
                      </p>
                      <p className="text-xs text-yellow-600">6AM - 12PM</p>
                    </div>
                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <p className="text-orange-600 text-sm">Afternoon</p>
                      <p className="text-xl font-bold text-orange-800">
                        {comprehensiveAnalytics.posting_times.optimal_posting_analysis.time_period_breakdown.afternoon?.percentage || 0}%
                      </p>
                      <p className="text-xs text-orange-600">12PM - 6PM</p>
                    </div>
                    <div className="text-center p-3 bg-purple-50 rounded-lg">
                      <p className="text-purple-600 text-sm">Evening</p>
                      <p className="text-xl font-bold text-purple-800">
                        {comprehensiveAnalytics.posting_times.optimal_posting_analysis.time_period_breakdown.evening?.percentage || 0}%
                      </p>
                      <p className="text-xs text-purple-600">6PM - 12AM</p>
                    </div>
                  </>
                ) : filteredInsights.optimal_posting_times?.time_period_breakdown ? (
                  <>
                    <div className="text-center p-3 bg-yellow-50 rounded-lg">
                      <p className="text-yellow-600 text-sm">Morning</p>
                      <p className="text-xl font-bold text-yellow-800">
                        {filteredInsights.optimal_posting_times.time_period_breakdown.morning?.percentage || 0}%
                      </p>
                      <p className="text-xs text-yellow-600">6AM - 12PM</p>
                    </div>
                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <p className="text-orange-600 text-sm">Afternoon</p>
                      <p className="text-xl font-bold text-orange-800">
                        {filteredInsights.optimal_posting_times.time_period_breakdown.afternoon?.percentage || 0}%
                      </p>
                      <p className="text-xs text-orange-600">12PM - 6PM</p>
                    </div>
                    <div className="text-center p-3 bg-purple-50 rounded-lg">
                      <p className="text-purple-600 text-sm">Evening</p>
                      <p className="text-xl font-bold text-purple-800">
                        {filteredInsights.optimal_posting_times.time_period_breakdown.evening?.percentage || 0}%
                      </p>
                      <p className="text-xs text-purple-600">6PM - 12AM</p>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="text-center p-3 bg-gray-100 rounded-lg">
                      <p className="text-gray-600 text-sm">Morning</p>
                      <p className="text-xl font-bold text-gray-800">N/A</p>
                      <p className="text-xs text-gray-600">6AM - 12PM</p>
                    </div>
                    <div className="text-center p-3 bg-gray-100 rounded-lg">
                      <p className="text-gray-600 text-sm">Afternoon</p>
                      <p className="text-xl font-bold text-gray-800">N/A</p>
                      <p className="text-xs text-gray-600">12PM - 6PM</p>
                    </div>
                    <div className="text-center p-3 bg-gray-100 rounded-lg">
                      <p className="text-gray-600 text-sm">Evening</p>
                      <p className="text-xl font-bold text-gray-800">N/A</p>
                      <p className="text-xs text-gray-600">6PM - 12AM</p>
                    </div>
                  </>
                )}
              </div>

              {/* Best Posting Time from Analytics Service */}
              <div className="p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
                <h4 className="text-sm font-medium text-green-800 mb-2">🎯 Recommended Posting Time</h4>
                <p className="text-lg font-bold text-green-900">
                  {comprehensiveAnalytics?.posting_times?.optimal_posting_analysis?.favoured_posting_time || 
                   filteredInsights.optimal_posting_times?.favoured_posting_time || 'Morning (9:00 AM - 11:00 AM)'}
                </p>
                <p className="text-xs text-green-700 mt-1">
                  Based on engagement patterns from your posts
                </p>
              </div>

              {/* Best Days from Analytics Service */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700">Best Performing Days</h4>
                <div className="grid grid-cols-7 gap-1">
                  {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map((fullDay, index) => {
                    const shortDay = fullDay.slice(0, 3);
                    const bestDays = comprehensiveAnalytics?.posting_times?.best_days || filteredInsights.optimal_posting_times?.best_days || [];
                    const dayData = bestDays.find(d => d.day === fullDay);
                    const isTopDay = dayData && bestDays.indexOf(dayData) < 3;
                    
                    return (
                      <div key={shortDay} className={`text-center p-2 rounded ${isTopDay ? 'bg-green-100' : 'bg-gray-50'}`}>
                        <p className="text-xs text-gray-600">{shortDay}</p>
                        <p className={`text-sm font-bold ${isTopDay ? 'text-green-800' : 'text-gray-900'}`}>
                          {dayData ? Math.round(dayData.avg_engagement) : 0}
                        </p>
                      </div>
                    );
                  })}
                </div>
                <p className="text-xs text-gray-500 text-center mt-2">
                  Average engagement per day (green = top performing)
                </p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No time data available</p>
                <p className="text-sm mt-2">Post more content to see time analysis</p>
              </div>
            </div>
          )}
        </div>

        {/* Advanced Performance Metrics */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            📊 Advanced Performance Metrics
          </h3>
          {filteredInsights ? (
            <div className="space-y-4">
              {/* Key Performance Indicators */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-blue-600 text-sm">Engagement Rate</p>
                  <p className="text-xl font-bold text-blue-800">
                    {comprehensiveAnalytics?.performance?.engagement_rate 
                      ? `${comprehensiveAnalytics.performance.engagement_rate}%`
                      : filteredInsights.basic_stats?.engagement_per_content 
                        ? `${((filteredInsights.basic_stats.engagement_per_content / (filteredInsights.basic_stats.total_content || 1)) * 100).toFixed(1)}%`
                        : '0%'
                    }
                  </p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-green-600 text-sm">Content Quality</p>
                  <p className="text-xl font-bold text-green-800">
                    {comprehensiveAnalytics?.performance?.content_quality 
                      ? `${comprehensiveAnalytics.performance.content_quality}/100`
                      : filteredInsights.performance_insights?.performance_score 
                        ? `${Math.round(filteredInsights.performance_insights.performance_score)}/100`
                        : 'N/A'
                    }
                  </p>
                </div>
              </div>

              {/* Content Performance Distribution */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-700">Content Performance Distribution</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center p-2 bg-green-50 rounded">
                    <span className="text-sm text-gray-700">High Performers (&gt;avg)</span>
                    <span className="text-sm font-bold text-green-700">
                      {filteredInsights.top_performers_count || 0} posts
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-yellow-50 rounded">
                    <span className="text-sm text-gray-700">Average Performers</span>
                    <span className="text-sm font-bold text-yellow-700">
                      {Math.max(0, (filteredInsights.basic_stats?.total_content || 0) - (filteredInsights.top_performers_count || 0) - Math.round((filteredInsights.basic_stats?.total_content || 0) * 0.2))} posts
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-red-50 rounded">
                    <span className="text-sm text-gray-700">Low Performers (&lt;50% avg)</span>
                    <span className="text-sm font-bold text-red-700">
                      {Math.round((filteredInsights.basic_stats?.total_content || 0) * 0.2)} posts
                    </span>
                  </div>
                </div>
              </div>

              {/* Missing Data Notice */}
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <h4 className="text-xs font-medium text-amber-800 mb-1">📊 Data Sources</h4>
                <div className="text-xs text-amber-700 space-y-1">
                  <p>✅ Engagement: Likes, Comments (from Instagram Basic Display API)</p>
                  <p>⚠️ Limited: Reach, Impressions (requires Instagram Business API)</p>
                  <p>🔄 Time analysis: Estimated based on posting patterns</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No performance data available</p>
                <p className="text-sm mt-2">Add more content to see advanced metrics</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Performance Insights */}
      {filteredInsights && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Performance Insights{selectedUsername && ` - ${selectedUsername}`}
            </h3>
            <div className="text-sm text-gray-500">
              Filtered by last {chartTimeRange} days • {filteredInsights.top_posts.length} posts analyzed
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Top Performing Posts */}
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-3">Top 5 Performing Posts</h4>
              <div className="space-y-3">
                {filteredInsights.top_posts.slice(0, 5).map((post, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-sm text-gray-600">
                          {post.media_type} • {post.engagement} engagement
                        </p>
                        <span className="text-xs text-gray-400">
                          {new Date(post.post_date).toLocaleDateString()}
                        </span>
                      </div>
                      {post.hashtags && post.hashtags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-2">
                          {post.hashtags.map((hashtag, idx) => (
                            <span key={idx} className="inline-block bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded-full">
                              {hashtag}
                            </span>
                          ))}
                        </div>
                      )}
                      <a 
                        href={post.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-instagram-purple hover:text-instagram-pink text-sm"
                      >
                        View Post
                      </a>
                    </div>
                    <div className="text-right ml-3">
                      <div className="flex items-center text-sm text-gray-500">
                        <Heart className="w-4 h-4 mr-1" />
                        {post.likes}
                      </div>
                      <div className="flex items-center text-sm text-gray-500">
                        <MessageCircle className="w-4 h-4 mr-1" />
                        {post.comments}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom Performing Posts */}
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-3">Bottom 5 Performing Posts</h4>
              <div className="space-y-3">
                {filteredInsights.bottom_posts.slice(0, 5).map((post, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-sm text-gray-600">
                          {post.media_type} • {post.engagement} engagement
                        </p>
                        <span className="text-xs text-gray-400">
                          {new Date(post.post_date).toLocaleDateString()}
                        </span>
                      </div>
                      {post.hashtags && post.hashtags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-2">
                          {post.hashtags.map((hashtag, idx) => (
                            <span key={idx} className="inline-block bg-red-100 text-red-800 text-xs px-2 py-0.5 rounded-full">
                              {hashtag}
                            </span>
                          ))}
                        </div>
                      )}
                      <a 
                        href={post.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-instagram-purple hover:text-instagram-pink text-sm"
                      >
                        View Post
                      </a>
                    </div>
                    <div className="text-right ml-3">
                      <div className="flex items-center text-sm text-gray-500">
                        <Heart className="w-4 h-4 mr-1" />
                        {post.likes}
                      </div>
                      <div className="flex items-center text-sm text-gray-500">
                        <MessageCircle className="w-4 h-4 mr-1" />
                        {post.comments}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
