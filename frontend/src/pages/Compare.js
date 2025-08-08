import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, ComposedChart, LineChart, Line, BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts';
import { BarChart, TrendingUp, Calendar, Users, Activity, Hash, Clock, Zap, Download, Settings, X } from 'lucide-react';

const Compare = () => {
  // State management
  const [availableProfiles, setAvailableProfiles] = useState([]);
  const [selectedProfiles, setSelectedProfiles] = useState([]);
  const [profilesData, setProfilesData] = useState({});
  const [chartTimeRange, setChartTimeRange] = useState(30);
  const [selectedMetrics, setSelectedMetrics] = useState({
    performance: true,
    contentType: true,
    timeAnalysis: true,
    hashtags: true,
    dailyTrends: true,
    postVsEngagement: true
  });
  const [loadingProfiles, setLoadingProfiles] = useState(new Set());
  const [showMetricsPanel, setShowMetricsPanel] = useState(false);

  // Available metrics for selection
  const availableMetrics = [
    { key: 'performance', label: '📊 Performance Metrics', description: 'Engagement rate, content quality, performance score' },
    { key: 'contentType', label: '🎯 Content Type Performance', description: 'Carousel vs Reel analysis' },
    { key: 'timeAnalysis', label: '⏰ Optimal Posting Times', description: 'Best times and periods for posting' },
    { key: 'hashtags', label: '📈 Hashtag Analysis', description: 'Trending hashtags and performance' },
    { key: 'dailyTrends', label: '📅 Daily Engagement Trends', description: 'Daily engagement patterns' },
    { key: 'postVsEngagement', label: '📊 Posts vs Engagement', description: 'Post count vs engagement correlation' }
  ];

  // Fetch available profiles on component mount
  useEffect(() => {
    fetchAvailableProfiles();
  }, []);

  const fetchAvailableProfiles = async () => {
    try {
      const response = await fetch('/api/profiles');
      if (response.ok) {
        const data = await response.json();
        setAvailableProfiles(data.data || []);
      }
    } catch (error) {
      console.error('Error fetching profiles:', error);
    }
  };

  const handleProfileToggle = (profileUsername) => {
    setSelectedProfiles(prev => {
      if (prev.includes(profileUsername)) {
        // Remove profile
        const newProfiles = prev.filter(p => p !== profileUsername);
        // Remove from data cache
        const newData = { ...profilesData };
        delete newData[profileUsername];
        setProfilesData(newData);
        return newProfiles;
      } else if (prev.length < 5) {
        // Add profile (max 5)
        return [...prev, profileUsername];
      }
      return prev;
    });
  };

  const handleMetricToggle = (metricKey) => {
    setSelectedMetrics(prev => ({
      ...prev,
      [metricKey]: !prev[metricKey]
    }));
  };

  const fetchProfileData = async (username) => {
    // Set loading for this specific profile
    setLoadingProfiles(prev => new Set([...prev, username]));
    
    try {
      const [comprehensiveRes, dailyChartRes, insightsRes] = await Promise.all([
        fetch(`/api/analytics/comprehensive?username=${username}&days=${chartTimeRange}`),
        fetch(`/api/analytics/daily-chart?username=${username}&days=${chartTimeRange}`),
        fetch(`/api/analytics/insights?username=${username}&days=${chartTimeRange}`)
      ]);

      const [comprehensive, dailyChart, insights] = await Promise.all([
        comprehensiveRes.json(),
        dailyChartRes.json(),
        insightsRes.json()
      ]);

      const profileData = {
        comprehensive: comprehensive.data || {},
        dailyMetrics: dailyChart.data || [],
        insights: insights.data || {},
        username: username
      };

      setProfilesData(prev => ({
        ...prev,
        [username]: profileData
      }));

    } catch (error) {
      console.error(`Error fetching data for ${username}:`, error);
    } finally {
      // Remove loading for this specific profile
      setLoadingProfiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(username);
        return newSet;
      });
    }
  };

  // Fetch data when profiles are selected or time range changes
  useEffect(() => {
    // Clear existing data when time range changes
    if (selectedProfiles.length > 0) {
      setProfilesData({});
    }
    
    selectedProfiles.forEach(username => {
      fetchProfileData(username);
    });
  }, [selectedProfiles, chartTimeRange]);

  // Quick comparison stats
  const generateQuickStats = () => {
    if (selectedProfiles.length < 2) return null;

    const stats = selectedProfiles.map(username => {
      const data = profilesData[username];
      if (!data) return null;

      return {
        username,
        engagementRate: data.comprehensive?.performance?.engagement_rate || 0,
        contentQuality: data.comprehensive?.performance?.content_quality || 0,
        performanceScore: data.comprehensive?.performance?.performance_score || 0,
        favouredMode: data.comprehensive?.media_types?.best_performing_type !== 'post' 
          ? data.comprehensive?.media_types?.best_performing_type 
          : 'N/A',
        totalPosts: Object.values(data.comprehensive?.media_types?.performance_by_type || {})
          .reduce((sum, type) => sum + (type.count || 0), 0)
      };
    }).filter(Boolean);

    if (stats.length < 2) return null;

    // Find best performers
    const bestEngagement = stats.reduce((max, current) => 
      current.engagementRate > max.engagementRate ? current : max
    );
    const bestQuality = stats.reduce((max, current) => 
      current.contentQuality > max.contentQuality ? current : max
    );
    const bestPerformance = stats.reduce((max, current) => 
      current.performanceScore > max.performanceScore ? current : max
    );

    return { stats, bestEngagement, bestQuality, bestPerformance };
  };

  const quickStats = generateQuickStats();

  // Generate comparison insights
  const generateInsights = () => {
    if (!quickStats || quickStats.stats.length < 2) return [];

    const insights = [];
    const stats = quickStats.stats;

    // Engagement rate insights
    const engagementRates = stats.map(s => s.engagementRate).sort((a, b) => b - a);
    const engagementDiff = engagementRates[0] - engagementRates[engagementRates.length - 1];
    if (engagementDiff > 1) {
      insights.push({
        type: 'engagement',
        message: `${quickStats.bestEngagement.username} has ${engagementDiff.toFixed(2)}% higher engagement rate than the lowest performer`,
        icon: '📈'
      });
    }

    // Content quality insights
    const qualityScores = stats.map(s => s.contentQuality).sort((a, b) => b - a);
    const qualityDiff = qualityScores[0] - qualityScores[qualityScores.length - 1];
    if (qualityDiff > 10) {
      insights.push({
        type: 'quality',
        message: `${quickStats.bestQuality.username} shows ${qualityDiff} points higher content quality score`,
        icon: '⭐'
      });
    }

    // Favoured mode insights
    const modes = stats.map(s => s.favouredMode);
    const modeCount = modes.reduce((acc, mode) => {
      acc[mode] = (acc[mode] || 0) + 1;
      return acc;
    }, {});
    const popularMode = Object.entries(modeCount).reduce((max, [mode, count]) => 
      count > max.count ? { mode, count } : max, { mode: '', count: 0 }
    );
    
    if (popularMode.count > 1) {
      insights.push({
        type: 'mode',
        message: `${popularMode.count} profiles prefer ${popularMode.mode} content format`,
        icon: '🎯'
      });
    }

    return insights;
  };

  const insights = generateInsights();

  // Check if all selected profiles have loaded their data
  const allProfilesLoaded = selectedProfiles.every(username => 
    profilesData[username] && !loadingProfiles.has(username)
  );
  const processProfileDailyMetrics = (dailyMetrics) => {
    if (!dailyMetrics || dailyMetrics.length === 0) return [];
    
    return dailyMetrics.map(day => ({
      date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      total_engagement: day.total_engagement || 0,
      posts_count: day.posts_count || 0,
      avg_engagement_per_post: day.posts_count > 0 ? (day.total_engagement / day.posts_count) : 0
    }));
  };

  const renderProfileCard = (username, index) => {
    const data = profilesData[username];
    const isLoading = loadingProfiles.has(username);
    
    if (isLoading || !data) {
      return (
        <div key={username} className="bg-gray-50 p-4 rounded-lg">
          <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4 rounded-lg mb-6">
            <h2 className="text-xl font-bold">@{username}</h2>
            <p className="text-purple-100">Loading analytics...</p>
          </div>
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
            <p className="mt-2 text-gray-600">Fetching data...</p>
          </div>
        </div>
      );
    }

    const { comprehensive, dailyMetrics, insights } = data;
    const processedDailyMetrics = processProfileDailyMetrics(dailyMetrics);

    // Prepare hashtag data
    const hashtagData = comprehensive?.hashtags?.trending_hashtags?.map(tag => ({
      hashtag: tag.hashtag.replace('#', ''),
      posts: tag.total_posts,
      totalEngagement: tag.total_engagement,
      avgEngagement: Math.round(tag.avg_engagement),
      engagement_display: tag.engagement_display
    })) || [];

    return (
      <div key={username} className="bg-gray-50 p-4 rounded-lg">
        {/* Profile Header */}
        <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4 rounded-lg mb-6">
          <h2 className="text-xl font-bold">@{username}</h2>
          <p className="text-purple-100">Analytics Overview</p>
        </div>

        {/* Performance Metrics */}
        {selectedMetrics.performance && (
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">📊 Performance Metrics</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <TrendingUp className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                <p className="text-sm text-blue-600">Engagement Rate</p>
                <p className="text-2xl font-bold text-blue-800">
                  {comprehensive?.performance?.engagement_rate?.toFixed(2) || 'N/A'}%
                </p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <Zap className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <p className="text-sm text-green-600">Content Quality</p>
                <p className="text-2xl font-bold text-green-800">
                  {comprehensive?.performance?.content_quality || 'N/A'}/100
                </p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <Activity className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                <p className="text-sm text-purple-600">Performance Score</p>
                <p className="text-2xl font-bold text-purple-800">
                  {comprehensive?.performance?.performance_score || 'N/A'}/100
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Content Type Performance */}
        {selectedMetrics.contentType && (
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🎯 Content Type Performance</h3>
            {comprehensive?.media_types?.performance_by_type ? (
              <div className="space-y-4">
                {Object.entries(comprehensive.media_types.performance_by_type)
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
                ))}
                
                {/* Favoured Mode */}
                <div className="mt-4 p-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg">
                  <p className="text-sm">🏆 Favoured Mode</p>
                  <p className="text-lg font-bold capitalize">
                    {comprehensive?.media_types?.best_performing_type !== 'post' 
                      ? comprehensive?.media_types?.best_performing_type || 'N/A'
                      : 'N/A'}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No content type data available</p>
            )}
          </div>
        )}

        {/* Time Analysis */}
        {selectedMetrics.timeAnalysis && (
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">⏰ Optimal Posting Times</h3>
            {comprehensive?.posting_times?.optimal_posting_analysis?.time_period_breakdown ? (
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-3 bg-yellow-50 rounded-lg">
                  <p className="text-yellow-600 text-sm">Morning</p>
                  <p className="text-xl font-bold text-yellow-800">
                    {comprehensive.posting_times.optimal_posting_analysis.time_period_breakdown.morning?.percentage || 0}%
                  </p>
                  <p className="text-xs text-yellow-600">6AM - 12PM</p>
                </div>
                <div className="text-center p-3 bg-orange-50 rounded-lg">
                  <p className="text-orange-600 text-sm">Afternoon</p>
                  <p className="text-xl font-bold text-orange-800">
                    {comprehensive.posting_times.optimal_posting_analysis.time_period_breakdown.afternoon?.percentage || 0}%
                  </p>
                  <p className="text-xs text-orange-600">12PM - 6PM</p>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <p className="text-purple-600 text-sm">Evening</p>
                  <p className="text-xl font-bold text-purple-800">
                    {comprehensive.posting_times.optimal_posting_analysis.time_period_breakdown.evening?.percentage || 0}%
                  </p>
                  <p className="text-xs text-purple-600">6PM - 12AM</p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No posting time data available</p>
            )}
          </div>
        )}

        {/* Hashtag Analysis */}
        {selectedMetrics.hashtags && (
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🔥 Top Hashtags</h3>
            {hashtagData.length > 0 ? (
              <div className="space-y-2">
                {hashtagData.slice(0, 5).map((hashtag, idx) => (
                  <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span className="text-sm font-medium text-purple-600">#{hashtag.hashtag}</span>
                    <div className="text-right">
                      <p className="text-xs text-gray-600">{hashtag.posts} posts</p>
                      <p className="text-sm font-bold">{hashtag.avgEngagement} avg</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No hashtag data available</p>
            )}
          </div>
        )}

        {/* Daily Engagement Trend */}
        {selectedMetrics.dailyTrends && (
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">📈 Daily Engagement Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={processedDailyMetrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" fontSize={10} />
                <YAxis yAxisId="left" />
                <YAxis 
                  yAxisId="right" 
                  orientation="right" 
                  domain={[0, 'dataMax']}
                  tickFormatter={(value) => Math.round(value)}
                  allowDecimals={false}
                />
                <Tooltip />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="total_engagement" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  name="Total Engagement"
                />
                <Bar 
                  yAxisId="right"
                  dataKey="posts_count" 
                  fill="rgba(130, 202, 157, 0.8)" 
                  name="Posts Count"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Posts vs Engagement */}
        {selectedMetrics.postVsEngagement && (
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">📊 Posts vs Engagement</h3>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={processedDailyMetrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" fontSize={10} />
                <YAxis yAxisId="left" />
                <YAxis 
                  yAxisId="right" 
                  orientation="right" 
                  domain={[0, 'dataMax']}
                  tickFormatter={(value) => Math.round(value)}
                  allowDecimals={false}
                />
                <Tooltip />
                <Bar 
                  yAxisId="right"
                  dataKey="posts_count" 
                  fill="#8884d8" 
                  name="Posts Count" 
                />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="avg_engagement_per_post" 
                  stroke="#82ca9d" 
                  strokeWidth={2}
                  name="Avg Engagement per Post"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📊 Profile Comparison</h1>
          <p className="text-gray-600">Compare analytics across multiple Instagram profiles side-by-side</p>
        </div>

        {/* Profile Selection */}
        <div className="bg-white rounded-lg shadow p-6 mb-6 no-print">
          <h2 className="text-xl font-medium text-gray-900 mb-4">Select Profiles to Compare (2-5 profiles)</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {availableProfiles.map(profile => (
              <div 
                key={profile.username}
                className={`cursor-pointer p-4 rounded-lg border-2 transition-all ${
                  selectedProfiles.includes(profile.username)
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
                onClick={() => handleProfileToggle(profile.username)}
              >
                <div className="text-center">
                  <Users className="h-8 w-8 mx-auto mb-2 text-gray-600" />
                  <p className="font-medium text-gray-900">@{profile.username}</p>
                  <p className="text-xs text-gray-500">{profile.post_count || 0} posts</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-4 text-sm text-gray-600">
            Selected: {selectedProfiles.length}/5 profiles
            {selectedProfiles.length < 2 && (
              <span className="text-red-600 ml-2">• Select at least 2 profiles</span>
            )}
          </div>
        </div>

        {/* Controls */}
        {selectedProfiles.length >= 2 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6 no-print">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Time Range */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">📅 Time Range</h3>
                <select
                  value={chartTimeRange}
                  onChange={(e) => setChartTimeRange(Number(e.target.value))}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                >
                  <option value={7}>Last 7 days</option>
                  <option value={14}>Last 14 days</option>
                  <option value={30}>Last 30 days</option>
                  <option value={60}>Last 60 days</option>
                  <option value={90}>Last 90 days</option>
                </select>
              </div>

              {/* Metric Selection */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">📊 Select Metrics to Compare</h3>
                <div className="grid grid-cols-1 gap-2">
                  {availableMetrics.map(metric => (
                    <label key={metric.key} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={selectedMetrics[metric.key]}
                        onChange={() => handleMetricToggle(metric.key)}
                        className="rounded border-gray-300"
                      />
                      <span className="text-sm font-medium">{metric.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Quick Comparison Summary */}
        {quickStats && allProfilesLoaded && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-medium text-gray-900 mb-4">🏆 Quick Comparison Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-blue-800 mb-2">Best Engagement Rate</h3>
                <p className="text-lg font-bold text-blue-900">@{quickStats.bestEngagement.username}</p>
                <p className="text-sm text-blue-700">{quickStats.bestEngagement.engagementRate.toFixed(2)}%</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-green-800 mb-2">Best Content Quality</h3>
                <p className="text-lg font-bold text-green-900">@{quickStats.bestQuality.username}</p>
                <p className="text-sm text-green-700">{quickStats.bestQuality.contentQuality}/100</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-purple-800 mb-2">Best Performance Score</h3>
                <p className="text-lg font-bold text-purple-900">@{quickStats.bestPerformance.username}</p>
                <p className="text-sm text-purple-700">{quickStats.bestPerformance.performanceScore}/100</p>
              </div>
            </div>
            
            {/* Detailed comparison table */}
            <div className="mt-6 overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Profile</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Engagement Rate</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Content Quality</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Performance Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Favoured Mode</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Posts</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {quickStats.stats.map((stat, index) => (
                    <tr key={stat.username} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">@{stat.username}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{stat.engagementRate.toFixed(2)}%</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{stat.contentQuality}/100</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{stat.performanceScore}/100</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">{stat.favouredMode}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{stat.totalPosts}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Comparison Insights */}
        {insights.length > 0 && allProfilesLoaded && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-medium text-gray-900 mb-4">💡 Comparison Insights</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {insights.map((insight, index) => (
                <div key={index} className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200">
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">{insight.icon}</span>
                    <p className="text-sm text-gray-700">{insight.message}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Comparison View */}
        {selectedProfiles.length >= 2 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-medium text-gray-900 mb-6">📈 Comparison Results</h2>
            
            {loadingProfiles.size > 0 && (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
                <p className="mt-2 text-gray-600">Loading data for {loadingProfiles.size} profile(s)...</p>
              </div>
            )}

            <div className={`
              grid gap-6
              ${selectedProfiles.length === 2 ? 'grid-cols-1 xl:grid-cols-2' : 
                selectedProfiles.length === 3 ? 'grid-cols-1 lg:grid-cols-2 xl:grid-cols-3' :
                selectedProfiles.length === 4 ? 'grid-cols-1 lg:grid-cols-2 xl:grid-cols-2' :
                selectedProfiles.length === 5 ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3' :
                'grid-cols-1 lg:grid-cols-2 xl:grid-cols-3'
              }
            `}>
              {selectedProfiles.map((username, index) => renderProfileCard(username, index))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {selectedProfiles.length === 0 && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-900 mb-2">Start Your Comparison</h3>
            <p className="text-gray-600">Select at least 2 profiles to begin comparing their analytics</p>
          </div>
        )}

        {selectedProfiles.length === 1 && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-900 mb-2">Select One More Profile</h3>
            <p className="text-gray-600">You need at least 2 profiles to start comparison</p>
          </div>
        )}

        {/* Floating Action Buttons */}
        {selectedProfiles.length >= 2 && (
          <div className="fixed bottom-6 right-6 flex flex-col gap-2 no-print">
            {/* Metrics Toggle Button */}
            <button
              onClick={() => setShowMetricsPanel(!showMetricsPanel)}
              className="bg-purple-500 hover:bg-purple-600 text-white p-3 rounded-full shadow-lg transition-all"
              title="Toggle Metrics Panel"
            >
              <Settings className="h-6 w-6" />
            </button>
            
            {/* Export Button */}
            <button
              onClick={() => window.print()}
              className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-full shadow-lg transition-all"
              title="Export Comparison"
            >
              <Download className="h-6 w-6" />
            </button>
          </div>
        )}

        {/* Floating Metrics Panel */}
        {showMetricsPanel && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 no-print">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">Select Metrics to Compare</h3>
                <button
                  onClick={() => setShowMetricsPanel(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-3">
                {availableMetrics.map(metric => (
                  <label key={metric.key} className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      checked={selectedMetrics[metric.key]}
                      onChange={() => handleMetricToggle(metric.key)}
                      className="mt-1 rounded border-gray-300"
                    />
                    <div>
                      <span className="text-sm font-medium text-gray-900">{metric.label}</span>
                      <p className="text-xs text-gray-500">{metric.description}</p>
                    </div>
                  </label>
                ))}
              </div>
              
              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowMetricsPanel(false)}
                  className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg text-sm"
                >
                  Apply Changes
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Compare;
