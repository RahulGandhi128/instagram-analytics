import React, { useState, useEffect, useCallback } from 'react';
import { Users, MessageCircle, Heart, TrendingUp, BarChart, Download } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart as RechartsBarChart, Bar, ComposedChart } from 'recharts';
import { analyticsAPI } from '../services/api';
import { useUsernames } from '../hooks/useUsernames';

const Dashboard = ({ showNotification }) => {
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
  
  const { usernames: allUsernames } = useUsernames();

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const params = { days: chartTimeRange };
      if (selectedUsername) params.username = selectedUsername;

      const [summaryRes, mediaRes, insightsRes] = await Promise.all([
        analyticsAPI.getSummaryStats(params), // Add params to summary stats
        analyticsAPI.getMedia(params),
        analyticsAPI.getInsights(params)
      ]);

      setSummaryStats(summaryRes.data.data);
      
      // Store media posts data for hashtag analysis
      const mediaData = mediaRes.data.data || [];
      setMediaPostsData(mediaData);
      
      // Generate chart data from media posts with full date range
      const chartData = generateChartData(mediaData, params.days);
      setDailyMetrics(chartData);
      
      // Generate hashtag performance data
      const hashtags = generateHashtagData(mediaData, params.days);
      setHashtagData(hashtags);
      
      // Generate cumulative hashtag performance data
      const cumulativeHashtags = generateCumulativeHashtagData(mediaData, params.days);
      setCumulativeHashtagData(cumulativeHashtags);
      
      setInsights(insightsRes.data.data);
      
      // Debug logging for chart data
      console.log('Dashboard Data Updated:', {
        selectedUsername,
        chartTimeRange,
        metricsCount: chartData?.length || 0,
        mediaPostsCount: mediaRes.data.data?.length || 0,
        sampleMetric: chartData?.[0]
      });
    } catch (error) {
      showNotification('Error loading dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  }, [chartTimeRange, selectedUsername, showNotification]);

  // Generate chart data with full date range from media posts
  const generateChartData = (mediaData, days) => {
    const chartData = [];
    const endDate = new Date();
    
    // Create array of all dates in the selected range
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(endDate.getDate() - i);
      const dateKey = date.toISOString().split('T')[0];
      
      chartData.push({
        date: dateKey,
        total_engagement: 0,
        posts_count: 0,
        avg_engagement_per_post: 0,
        total_likes: 0,
        total_comments: 0
      });
    }
    
    // Aggregate media data by date
    mediaData.forEach(post => {
      if (post.post_datetime_ist) {
        const postDate = new Date(post.post_datetime_ist).toISOString().split('T')[0];
        const dayData = chartData.find(day => day.date === postDate);
        
        if (dayData) {
          dayData.posts_count += 1;
          dayData.total_engagement += (post.like_count || 0) + (post.comment_count || 0);
          dayData.total_likes += (post.like_count || 0);
          dayData.total_comments += (post.comment_count || 0);
        }
      }
    });
    
    // Calculate averages for days with posts
    chartData.forEach(day => {
      if (day.posts_count > 0) {
        day.avg_engagement_per_post = Math.round(day.total_engagement / day.posts_count);
      }
    });
    
    return chartData;
  };

  // Generate hashtag performance data from media posts
  const generateHashtagData = (mediaData, days) => {
    const hashtagPerformance = {};
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    console.log('Generating hashtag data:', { 
      totalPosts: mediaData.length, 
      cutoffDate: cutoffDate.toDateString() 
    });
    
    let postsWithCaptions = 0;
    let totalHashtagsFound = 0;
    
    mediaData.forEach(post => {
      // Filter by date range
      if (post.post_datetime_ist && new Date(post.post_datetime_ist) < cutoffDate) {
        return;
      }
      
      // Extract hashtags from caption
      if (post.caption) {
        postsWithCaptions++;
        const hashtags = post.caption.match(/#\w+/g) || [];
        totalHashtagsFound += hashtags.length;
        
        hashtags.forEach(hashtag => {
          const cleanHashtag = hashtag.toLowerCase();
          if (!hashtagPerformance[cleanHashtag]) {
            hashtagPerformance[cleanHashtag] = {
              hashtag: cleanHashtag,
              posts: 0,
              totalEngagement: 0,
              totalLikes: 0,
              totalComments: 0,
              avgEngagement: 0,
              usageCount: 0
            };
          }
          
          hashtagPerformance[cleanHashtag].posts += 1;
          hashtagPerformance[cleanHashtag].usageCount += 1; // Count each usage
          hashtagPerformance[cleanHashtag].totalEngagement += (post.like_count || 0) + (post.comment_count || 0);
          hashtagPerformance[cleanHashtag].totalLikes += (post.like_count || 0);
          hashtagPerformance[cleanHashtag].totalComments += (post.comment_count || 0);
        });
      }
    });
    
    console.log('Hashtag analysis:', { 
      postsWithCaptions, 
      totalHashtagsFound, 
      uniqueHashtags: Object.keys(hashtagPerformance).length 
    });
    
    // Calculate averages and return top hashtags
    const hashtagArray = Object.values(hashtagPerformance).map(data => ({
      ...data,
      avgEngagement: data.posts > 0 ? Math.round(data.totalEngagement / data.posts) : 0
    }));
    
    // Return top 10 hashtags by engagement (lowered minimum posts to 1)
    const filteredHashtags = hashtagArray
      .filter(h => h.posts >= 1) // Only hashtags used in 1+ posts
      .sort((a, b) => b.avgEngagement - a.avgEngagement)
      .slice(0, 10);
    
    console.log('Top hashtags:', filteredHashtags);
    
    return filteredHashtags;
  };

  // Generate cumulative hashtag data (total engagement, not average)
  const generateCumulativeHashtagData = (mediaData, days) => {
    const hashtagPerformance = {};
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    mediaData.forEach(post => {
      // Filter by date range
      if (post.post_datetime_ist && new Date(post.post_datetime_ist) < cutoffDate) {
        return;
      }
      
      // Extract hashtags from caption
      if (post.caption) {
        const hashtags = post.caption.match(/#\w+/g) || [];
        
        hashtags.forEach(hashtag => {
          const cleanHashtag = hashtag.toLowerCase();
          if (!hashtagPerformance[cleanHashtag]) {
            hashtagPerformance[cleanHashtag] = {
              hashtag: cleanHashtag,
              totalEngagement: 0,
              usageCount: 0,
              totalLikes: 0,
              totalComments: 0
            };
          }
          
          hashtagPerformance[cleanHashtag].usageCount += 1; // Count each usage
          hashtagPerformance[cleanHashtag].totalEngagement += (post.like_count || 0) + (post.comment_count || 0);
          hashtagPerformance[cleanHashtag].totalLikes += (post.like_count || 0);
          hashtagPerformance[cleanHashtag].totalComments += (post.comment_count || 0);
        });
      }
    });
    
    // Return top 10 hashtags by total engagement
    const hashtagArray = Object.values(hashtagPerformance);
    const filteredHashtags = hashtagArray
      .filter(h => h.usageCount >= 1)
      .sort((a, b) => b.totalEngagement - a.totalEngagement)
      .slice(0, 10);
    
    console.log('Top cumulative hashtags:', filteredHashtags);
    
    return filteredHashtags;
  };

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

  const usernames = Object.keys(insights);
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
        </div>
      </div>

      {/* Debug Info - Remove this in production */}
      <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
        <p><strong>Debug Info:</strong> Selected: "{selectedUsername || 'All'}" | Time: {chartTimeRange} days | Chart Data: {processedDailyMetrics.length} days</p>
        <p><strong>Date Range:</strong> {processedDailyMetrics[0]?.date} to {processedDailyMetrics[processedDailyMetrics.length - 1]?.date}</p>
        <p><strong>Posts Found:</strong> {processedDailyMetrics.reduce((sum, day) => sum + day.posts_count, 0)} total posts | Unique Hashtags: {hashtagData.length} | Total Hashtag Usage: {cumulativeHashtagData.reduce((sum, h) => sum + h.usageCount, 0)}</p>
      </div>

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
              <YAxis yAxisId="right" orientation="right" />
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
            <RechartsBarChart data={processedDailyMetrics}>
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
                formatter={(value, name) => [value, name]}
              />
              <Legend />
              <Bar dataKey="posts_count" fill="#8884d8" name="Posts Count" />
              <Bar dataKey="avg_engagement_per_post" fill="#82ca9d" name="Avg Engagement per Post" />
            </RechartsBarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts - Second Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Unique Hashtag Performance */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Top Unique Hashtags - Average Engagement ({chartTimeRange} days)
          </h3>
          {hashtagData.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <RechartsBarChart data={hashtagData}>
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
                  formatter={(value, name) => [value, name]}
                  labelFormatter={(label) => `${label} (used in ${hashtagData.find(h => h.hashtag === label)?.posts || 0} posts)`}
                />
                <Legend />
                <Bar dataKey="avgEngagement" fill="#E1306C" name="Avg Engagement per Post" />
              </RechartsBarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No hashtag data available</p>
                <p className="text-sm mt-2">Add captions with hashtags to your posts to see hashtag performance</p>
              </div>
            </div>
          )}
        </div>

        {/* Cumulative Hashtag Performance */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Top Hashtags - Total Engagement ({chartTimeRange} days)
          </h3>
          {cumulativeHashtagData.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <RechartsBarChart data={cumulativeHashtagData}>
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
                  formatter={(value, name) => [value, name]}
                  labelFormatter={(label) => `${label} (used ${cumulativeHashtagData.find(h => h.hashtag === label)?.usageCount || 0} times)`}
                />
                <Legend />
                <Bar dataKey="totalEngagement" fill="#FF6B35" name="Total Engagement" />
              </RechartsBarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No hashtag data available</p>
                <p className="text-sm mt-2">Add captions with hashtags to your posts to see hashtag performance</p>
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
