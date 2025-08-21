import React, { useState, useEffect, useCallback } from 'react';
import { Users, MessageCircle, Heart, TrendingUp, BarChart, Eye, Zap } from 'lucide-react';
import { XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area, Line } from 'recharts';
import { analyticsAPI } from '../services/api';
import { useUsernames } from '../hooks/useUsernames';


const Dashboard = ({ showNotification }) => {

  const [analyticsData, setAnalyticsData] = useState(null);
  const [selectedUsername, setSelectedUsername] = useState('');
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);
  const [fetchingData, setFetchingData] = useState(false);
  
  const { usernames: allUsernames } = useUsernames();

  const fetchAnalyticsData = useCallback(async () => {
    if (!selectedUsername) {
      setAnalyticsData(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const params = { days: timeRange, username: selectedUsername };

      // Fetch comprehensive analytics data
      const [summaryRes, comprehensiveRes, dailyRes] = await Promise.all([
        analyticsAPI.getSummaryStats(params),
        fetch(`http://localhost:5000/api/analytics/comprehensive?${new URLSearchParams(params)}`).then(r => r.json()),
        fetch(`http://localhost:5000/api/analytics/daily-chart?${new URLSearchParams(params)}`).then(r => r.json())
      ]);

      const data = {
        summary: summaryRes.data,
        comprehensive: comprehensiveRes.success ? comprehensiveRes.data : null,
        daily: dailyRes.success ? dailyRes.data : []
      };

      setAnalyticsData(data);
    } catch (error) {
      console.error('Error loading analytics data:', error);
      showNotification('Error loading dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  }, [timeRange, selectedUsername, showNotification]);

  useEffect(() => {
    fetchAnalyticsData();
  }, [fetchAnalyticsData]);

  const fetchInstagramData = async () => {
    setFetchingData(true);
    try {
      showNotification('Fetching latest Instagram data...', 'info');
      const response = await fetch('http://localhost:5000/api/fetch-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      const data = await response.json();
      
      if (data.success) {
        showNotification('✅ Instagram data updated successfully!', 'success');
        await fetchAnalyticsData();
      } else {
        showNotification(`Error: ${data.error}`, 'error');
      }
    } catch (error) {
      showNotification('Error fetching Instagram data', 'error');
    } finally {
      setFetchingData(false);
    }
  };

  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };



  if (!selectedUsername) {
    return (
      <div className="px-4 py-6 sm:px-0">
        {/* Header */}
        <div className="md:flex md:items-center md:justify-between mb-6">
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
              📊 Analytics Dashboard
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              Comprehensive Instagram performance analytics and insights
            </p>
          </div>
          <div className="mt-4 flex md:mt-0 md:ml-4 space-x-3">
            <select
              value={selectedUsername}
              onChange={(e) => setSelectedUsername(e.target.value)}
              className="rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value="">Select a Profile</option>
              {allUsernames.map(username => (
                <option key={username} value={username}>{username}</option>
              ))}
            </select>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(parseInt(e.target.value))}
              className="rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
            <button
              onClick={fetchInstagramData}
              disabled={fetchingData}
              className="inline-flex items-center px-4 py-2 bg-instagram-purple text-white rounded-md hover:bg-instagram-pink disabled:opacity-50"
            >
              {fetchingData ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Fetching...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Fetch Data
                </>
              )}
            </button>
          </div>
        </div>

        {/* No Username Selected Message */}
        <div className="flex justify-center items-center h-96">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-gray-100 mb-4">
              <BarChart className="h-6 w-6 text-gray-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Profile to View Analytics</h3>
            <p className="text-gray-500 mb-4">
              Choose a profile from the dropdown above to see comprehensive analytics and insights.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
              <h4 className="text-sm font-medium text-blue-800 mb-2">📊 Available Analytics:</h4>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• Total Reach, Impressions & Engagement</li>
                <li>• Content Type Performance (Posts, Reels, Carousels)</li>
                <li>• Favoured Time of Posting Analysis</li>
                <li>• Top Performer Content</li>
                <li>• Collaboration Content Metrics</li>
                <li>• Engagement Trends & Daily Charts</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-instagram-purple"></div>
      </div>
    );
  }

  const data = analyticsData;
  const comprehensive = data?.comprehensive;
  const summary = data?.summary;
  const dailyData = data?.daily || [];

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between mb-6">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            📊 Analytics Dashboard
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Comprehensive Instagram performance analytics and insights
          </p>
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4 space-x-3">
                     <select
             value={selectedUsername}
             onChange={(e) => setSelectedUsername(e.target.value)}
             className="rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
           >
             <option value="">Select a Profile</option>
             {allUsernames.map(username => (
               <option key={username} value={username}>{username}</option>
             ))}
           </select>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(parseInt(e.target.value))}
            className="rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
          >
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button
            onClick={fetchInstagramData}
            disabled={fetchingData}
            className="inline-flex items-center px-4 py-2 bg-instagram-purple text-white rounded-md hover:bg-instagram-pink disabled:opacity-50"
          >
            {fetchingData ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Fetching...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 mr-2" />
                Fetch Data
              </>
            )}
          </button>
        </div>
      </div>

      {/* Primary Analytics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Reach */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Reach</p>
              <p className="text-3xl font-bold">
                {formatNumber(comprehensive?.reach?.total_reach || summary?.total_reach || 0)}
              </p>
              <p className="text-blue-100 text-xs">Unique accounts reached</p>
            </div>
            <Eye className="h-8 w-8 text-blue-200" />
          </div>
        </div>

        {/* Total Impressions */}
        <div className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Total Impressions</p>
              <p className="text-3xl font-bold">
                {formatNumber(comprehensive?.impressions?.total_impressions || summary?.total_impressions || 0)}
              </p>
              <p className="text-green-100 text-xs">Total times viewed</p>
            </div>
            <BarChart className="h-8 w-8 text-green-200" />
          </div>
        </div>

        {/* Total Engagement */}
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Total Engagement</p>
              <p className="text-3xl font-bold">
                {formatNumber(comprehensive?.engagement?.total_engagement || summary?.total_engagement || 0)}
              </p>
              <p className="text-purple-100 text-xs">Likes + Comments + Shares</p>
            </div>
            <Heart className="h-8 w-8 text-purple-200" />
          </div>
        </div>

        {/* Total Content */}
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Total Content</p>
              <p className="text-3xl font-bold">
                {formatNumber(comprehensive?.content?.total_content || summary?.total_posts || 0)}
              </p>
              <p className="text-orange-100 text-xs">Posts + Reels + Carousels</p>
            </div>
            <Users className="h-8 w-8 text-orange-200" />
          </div>
        </div>
      </div>

      {/* Secondary Analytics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Impression Per Content Ratio */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-center">
            <BarChart className="h-8 w-8 text-blue-500 mx-auto mb-2" />
            <p className="text-gray-600 text-sm">Impression Per Content</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatNumber(comprehensive?.impressions?.impression_per_content || 0)}
            </p>
            <p className="text-xs text-gray-500">Avg per piece</p>
          </div>
        </div>

        {/* Engagement Per Content */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-center">
            <TrendingUp className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <p className="text-gray-600 text-sm">Engagement Per Content</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatNumber(comprehensive?.engagement?.engagement_per_content || 0)}
            </p>
            <p className="text-xs text-gray-500">Avg per piece</p>
          </div>
        </div>

        {/* Total Comments */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-center">
            <MessageCircle className="h-8 w-8 text-purple-500 mx-auto mb-2" />
            <p className="text-gray-600 text-sm">Total Comments</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatNumber(comprehensive?.engagement?.total_comments || summary?.total_comments || 0)}
            </p>
            <p className="text-xs text-gray-500">User interactions</p>
          </div>
        </div>

        {/* Average Reel Views */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-center">
            <Eye className="h-8 w-8 text-orange-500 mx-auto mb-2" />
            <p className="text-gray-600 text-sm">Avg Reel Views</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatNumber(comprehensive?.reels?.average_reel_views || 0)}
            </p>
            <p className="text-xs text-gray-500">Per reel</p>
          </div>
        </div>
      </div>

      {/* Content Type Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Favoured Content Type */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            🎯 Favoured Content Type
          </h3>
          {comprehensive?.content_types ? (
            <div className="space-y-4">
              {Object.entries(comprehensive.content_types.breakdown || {})
                .filter(([type, data]) => data.count > 0)
                .map(([type, data]) => (
                <div key={type} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 capitalize">{type}</p>
                    <p className="text-xs text-gray-500">{data.count} posts • {formatNumber(data.total_engagement)} engagement</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900">{formatNumber(data.avg_engagement)}</p>
                    <p className="text-xs text-gray-500">avg engagement</p>
                  </div>
                </div>
              ))}
              
              <div className="mt-4 p-4 bg-gradient-to-r from-instagram-purple to-instagram-pink text-white rounded-lg">
                <p className="text-sm">🏆 Best Performing Type</p>
                <p className="text-lg font-bold capitalize">
                  {comprehensive.content_types.best_performing_type || 'N/A'}
                </p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No content type data available</p>
                <p className="text-sm mt-2">Post content to see type analysis</p>
              </div>
            </div>
          )}
        </div>

        {/* Content Type Distribution Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            📊 Content Type Distribution
          </h3>
          {comprehensive?.content_types?.breakdown ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={Object.entries(comprehensive.content_types.breakdown)
                    .filter(([type, data]) => data.count > 0)
                    .map(([type, data]) => ({
                      name: type,
                      value: data.count,
                      engagement: data.total_engagement
                    }))}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {Object.entries(comprehensive.content_types.breakdown)
                    .filter(([type, data]) => data.count > 0)
                    .map((entry, index) => {
                    const colors = ['#E1306C', '#FF6B35', '#4285F4', '#34A853', '#9C27B0'];
                    return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                  })}
                </Pie>
                <Tooltip 
                  formatter={(value, name, props) => [
                    `${value} posts`,
                    `${props.payload.name} (${formatNumber(props.payload.engagement)} engagement)`
                  ]}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No content type data available</p>
                <p className="text-sm mt-2">Post content to see distribution</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Time Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Favoured Time of Posting */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            🕐 Favoured Time of Posting
          </h3>
          {comprehensive?.posting_times ? (
            <div className="space-y-4">
              {/* Time Period Breakdown */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center p-3 bg-yellow-50 rounded-lg">
                  <p className="text-yellow-600 text-sm">Morning</p>
                  <p className="text-xl font-bold text-yellow-800">
                    {comprehensive.posting_times.time_period_breakdown?.morning?.percentage || 0}%
                  </p>
                  <p className="text-xs text-yellow-600">6AM - 12PM</p>
                </div>
                <div className="text-center p-3 bg-orange-50 rounded-lg">
                  <p className="text-orange-600 text-sm">Afternoon</p>
                  <p className="text-xl font-bold text-orange-800">
                    {comprehensive.posting_times.time_period_breakdown?.afternoon?.percentage || 0}%
                  </p>
                  <p className="text-xs text-orange-600">12PM - 6PM</p>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <p className="text-purple-600 text-sm">Evening</p>
                  <p className="text-xl font-bold text-purple-800">
                    {comprehensive.posting_times.time_period_breakdown?.evening?.percentage || 0}%
                  </p>
                  <p className="text-xs text-purple-600">6PM - 12AM</p>
                </div>
              </div>

              {/* Best Posting Time */}
              <div className="p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
                <h4 className="text-sm font-medium text-green-800 mb-2">🎯 Recommended Posting Time</h4>
                <p className="text-lg font-bold text-green-900">
                  {comprehensive.posting_times.favoured_posting_time || 'Morning (9:00 AM - 11:00 AM)'}
                </p>
                <p className="text-xs text-green-700 mt-1">
                  Based on engagement patterns
                </p>
              </div>

              {/* Best Days */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700">Best Performing Days</h4>
                <div className="grid grid-cols-7 gap-1">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => {
                    const dayData = comprehensive.posting_times.best_days?.[index];
                    const isTopDay = dayData && comprehensive.posting_times.best_days.indexOf(dayData) < 3;
                    
                    return (
                      <div key={day} className={`text-center p-2 rounded ${isTopDay ? 'bg-green-100' : 'bg-gray-50'}`}>
                        <p className="text-xs text-gray-600">{day}</p>
                        <p className={`text-sm font-bold ${isTopDay ? 'text-green-800' : 'text-gray-900'}`}>
                          {dayData ? Math.round(dayData.avg_engagement) : 0}
                        </p>
                      </div>
                    );
                  })}
                </div>
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

        {/* Engagement Trend */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            📈 Engagement Trend ({timeRange} days)
          </h3>
          {dailyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={dailyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  fontSize={12}
                />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    formatNumber(value),
                    name === 'total_engagement' ? 'Total Engagement' : 'Posts Count'
                  ]}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="total_engagement" 
                  stroke="#8884d8" 
                  fill="#8884d8"
                  fillOpacity={0.3}
                  name="Total Engagement"
                />
                <Line 
                  type="monotone" 
                  dataKey="posts_count" 
                  stroke="#82ca9d" 
                  strokeWidth={2}
                  name="Posts Count"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No trend data available</p>
                <p className="text-sm mt-2">Post content to see engagement trends</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Top Performer Content */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            🏆 Top Performer Content
          </h3>
          {comprehensive?.top_performers ? (
            <div className="space-y-3">
              {comprehensive.top_performers.slice(0, 5).map((post, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm text-gray-600 capitalize">
                        {post.media_type} • {formatNumber(post.engagement)} engagement
                      </p>
                      <span className="text-xs text-gray-400">
                        {new Date(post.post_date).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-900 truncate">{post.caption?.substring(0, 50)}...</p>
                  </div>
                  <div className="text-right ml-3">
                    <div className="flex items-center text-sm text-gray-500">
                      <Heart className="w-4 h-4 mr-1" />
                      {formatNumber(post.likes)}
                    </div>
                    <div className="flex items-center text-sm text-gray-500">
                      <MessageCircle className="w-4 h-4 mr-1" />
                      {formatNumber(post.comments)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No top performers data</p>
                <p className="text-sm mt-2">Post content to see top performers</p>
              </div>
            </div>
          )}
        </div>

        {/* Collaboration Content */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            🤝 Collaboration Content
          </h3>
          {comprehensive?.collaborations ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-blue-600 text-sm">Total Collabs</p>
                  <p className="text-2xl font-bold text-blue-800">
                    {comprehensive.collaborations.total_collaborations || 0}
                  </p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-green-600 text-sm">Collab Engagement</p>
                  <p className="text-2xl font-bold text-green-800">
                    {formatNumber(comprehensive.collaborations.total_collab_engagement || 0)}
                  </p>
                </div>
              </div>
              
              <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
                <h4 className="text-sm font-medium text-purple-800 mb-2">📊 Collaboration Performance</h4>
                <p className="text-lg font-bold text-purple-900">
                  {formatNumber(comprehensive.collaborations.avg_collab_engagement || 0)} avg engagement
                </p>
                <p className="text-xs text-purple-700 mt-1">
                  Per collaboration post
                </p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p className="text-lg">No collaboration data</p>
                <p className="text-sm mt-2">Collaborate with others to see metrics</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Data Availability Notice */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-medium text-yellow-800 mb-2">📊 Data Availability Status</h4>
        <div className="text-xs text-yellow-700 grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div>
            <p className="font-medium mb-1">✅ Available Metrics:</p>
            <p>• Total Content, Engagement, Likes, Comments</p>
            <p>• Content Type Distribution</p>
            <p>• Collaboration Content Count</p>
            <p>• Time Analysis & Posting Patterns</p>
            <p>• Top Performers & Performance Trends</p>
          </div>
          <div>
            <p className="font-medium mb-1">⚠️ Limited Metrics:</p>
            <p>• Reel Views (using available play_count)</p>
            <p>• Shares (using reshare_count)</p>
            <p>• Detailed Time Analytics</p>
          </div>
          <div>
            <p className="font-medium mb-1">❌ Missing (Requires Business API):</p>
            <p>• Total Reach & Impressions</p>
            <p>• Impression Per Content</p>
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
  );
};

export default Dashboard;
