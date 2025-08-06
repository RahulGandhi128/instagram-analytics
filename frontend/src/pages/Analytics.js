import React, { useState, useEffect } from 'react';
import { TrendingUp, Clock, BarChart3, PieChart, Calendar, Target } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Cell, Pie } from 'recharts';
import { analyticsAPI } from '../services/api';
import { useUsernames } from '../hooks/useUsernames';

const Analytics = ({ showNotification }) => {
  const [insights, setInsights] = useState({});
  const [weeklyComparison, setWeeklyComparison] = useState({});
  const [selectedUsername, setSelectedUsername] = useState('');
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);
  const [comparisonPeriod, setComparisonPeriod] = useState('week');
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');
  
  const { usernames: allUsernames } = useUsernames();

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      const params = { days: timeRange };
      if (selectedUsername) params.username = selectedUsername;

      // Prepare comparison parameters
      const comparisonParams = { period: comparisonPeriod };
      if (selectedUsername) comparisonParams.username = selectedUsername;
      
      // Add custom date range if selected
      if (comparisonPeriod === 'custom' && customStartDate && customEndDate) {
        comparisonParams.start_date = customStartDate;
        comparisonParams.end_date = customEndDate;
      }

      const [insightsRes, weeklyRes] = await Promise.all([
        analyticsAPI.getInsights(params),
        analyticsAPI.getWeeklyComparison(comparisonParams)
      ]);

      setInsights(insightsRes.data.data);
      setWeeklyComparison(weeklyRes.data.data);
      
      // Debug logging
      console.log('Analytics Data Updated:', {
        selectedUsername,
        timeRange,
        comparisonPeriod,
        customDates: comparisonPeriod === 'custom' ? { start: customStartDate, end: customEndDate } : null,
        weeklyComparisonData: weeklyRes.data.data
      });
    } catch (error) {
      showNotification('Error loading analytics data', 'error');
      console.error('Analytics error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData();
    
    // Listen for global data fetch events
    const handleDataFetched = () => {
      fetchAnalyticsData();
    };
    
    window.addEventListener('dataFetched', handleDataFetched);
    
    return () => {
      window.removeEventListener('dataFetched', handleDataFetched);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedUsername || timeRange || comparisonPeriod || 
        (comparisonPeriod === 'custom' && customStartDate && customEndDate)) {
      fetchAnalyticsData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedUsername, timeRange, comparisonPeriod, customStartDate, customEndDate]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-instagram-purple"></div>
      </div>
    );
  }

  const usernames = Object.keys(insights);
  const currentUserInsights = selectedUsername && insights[selectedUsername] ? insights[selectedUsername] : null;

  // Prepare data for charts
  const optimalTimesData = currentUserInsights?.optimal_posting_times || [];
  const mediaTypeData = currentUserInsights?.media_type_analysis ? 
    Object.entries(currentUserInsights.media_type_analysis).map(([type, stats]) => ({
      name: type,
      posts: stats.count,
      avgEngagement: stats.avg_engagement
    })) : [];

  // Colors for charts
  const COLORS = ['#E1306C', '#833AB4', '#FD1D1D', '#F77737'];

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between mb-6">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Advanced Analytics
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Deep insights into content performance and optimal strategies
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Account
            </label>
            <select
              value={selectedUsername}
              onChange={(e) => setSelectedUsername(e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value="">Select Account</option>
              {allUsernames.map(username => (
                <option key={username} value={username}>{username}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Data Time Range
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(parseInt(e.target.value))}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Comparison Period
            </label>
            <select
              value={comparisonPeriod}
              onChange={(e) => setComparisonPeriod(e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value="week">Week over Week</option>
              <option value="month">Month over Month</option>
              <option value="custom">Custom Period</option>
            </select>
          </div>
        </div>

        {/* Custom Date Range Picker */}
        {comparisonPeriod === 'custom' && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Custom Date Range</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={customStartDate}
                  onChange={(e) => setCustomStartDate(e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
                  max={new Date().toISOString().split('T')[0]}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={customEndDate}
                  onChange={(e) => setCustomEndDate(e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
                  max={new Date().toISOString().split('T')[0]}
                  min={customStartDate}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Debug Info - Remove this in production */}
      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
        <p><strong>Analytics Debug:</strong> User: "{selectedUsername || 'None'}" | Time: {timeRange}d | Comparison: {comparisonPeriod}
          {comparisonPeriod === 'custom' && customStartDate && customEndDate && 
            ` (${customStartDate} to ${customEndDate})`
          }
        </p>
      </div>

      {!selectedUsername ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <Target className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Select an Account</h3>
          <p className="text-gray-500">Choose an account from the dropdown above to view detailed analytics</p>
        </div>
      ) : !currentUserInsights ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <BarChart3 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Data Available</h3>
          <p className="text-gray-500">No analytics data found for the selected account and time range</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-blue-100">
                  <BarChart3 className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Posts</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {currentUserInsights.basic_stats?.total_posts || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-red-100">
                  <TrendingUp className="h-6 w-6 text-red-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Avg Engagement</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {currentUserInsights.basic_stats?.avg_engagement?.toFixed(1) || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-green-100">
                  <Target className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Likes</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {currentUserInsights.basic_stats?.total_likes?.toLocaleString() || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-purple-100">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Comments</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {currentUserInsights.basic_stats?.total_comments?.toLocaleString() || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Optimal Posting Times */}
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center mb-4">
                <Clock className="h-5 w-5 text-instagram-purple mr-2" />
                <h3 className="text-lg font-medium text-gray-900">Optimal Posting Times (IST)</h3>
              </div>
              {optimalTimesData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={optimalTimesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" />
                    <YAxis />
                    <Tooltip formatter={(value, name) => [value.toFixed(1), 'Avg Engagement']} />
                    <Bar dataKey="avg_engagement" fill="#E1306C" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-300 flex items-center justify-center text-gray-500">
                  No timing data available
                </div>
              )}
              <p className="text-xs text-gray-500 mt-2 text-center">
                * Times shown in Indian Standard Time (IST)
              </p>
            </div>

            {/* Media Type Performance */}
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center mb-4">
                <PieChart className="h-5 w-5 text-instagram-purple mr-2" />
                <h3 className="text-lg font-medium text-gray-900">Media Type Performance</h3>
              </div>
              {mediaTypeData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      dataKey="avgEngagement"
                      data={mediaTypeData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      label={({name, value}) => `${name}: ${value.toFixed(1)}`}
                    >
                      {mediaTypeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-300 flex items-center justify-center text-gray-500">
                  No media type data available
                </div>
              )}
            </div>
          </div>

          {/* Weekly Comparison */}
          {weeklyComparison[selectedUsername] && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Recent Period Comparison
                {weeklyComparison[selectedUsername].date_range && (
                  <span className="text-sm font-normal text-gray-500 ml-2">
                    (Based on most recent posts)
                  </span>
                )}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Recent Period Posts</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {weeklyComparison[selectedUsername].current_week?.total_posts || 0}
                  </p>
                  <p className="text-sm text-gray-500">
                    vs {weeklyComparison[selectedUsername].previous_week?.total_posts || 0} previous period
                  </p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Recent Period Engagement</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {weeklyComparison[selectedUsername].current_week?.total_engagement?.toLocaleString() || 0}
                  </p>
                  <p className={`text-sm ${
                    (weeklyComparison[selectedUsername].changes?.engagement_change_percent || 0) >= 0 
                      ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {(weeklyComparison[selectedUsername].changes?.engagement_change_percent || 0) >= 0 ? '+' : ''}
                    {weeklyComparison[selectedUsername].changes?.engagement_change_percent?.toFixed(1) || 0}%
                  </p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Avg Engagement per Post</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {weeklyComparison[selectedUsername].current_week?.avg_engagement_per_post?.toFixed(1) || 0}
                  </p>
                  <p className="text-sm text-gray-500">
                    vs {weeklyComparison[selectedUsername].previous_week?.avg_engagement_per_post?.toFixed(1) || 0} previous
                  </p>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-4 text-center">
                * All times are in IST (Indian Standard Time) • Comparison based on available post data
              </p>
            </div>
          )}

          {/* Best Times Recommendations */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">📈 Recommendations</h3>
            <div className="space-y-3">
              <div className="p-4 bg-green-50 rounded-lg">
                <h4 className="font-medium text-green-900 mb-2">🕒 Best Posting Times (IST)</h4>
                <p className="text-green-700 text-sm">
                  {optimalTimesData.length > 0 
                    ? `Post at ${optimalTimesData[0]?.hour} IST for highest engagement (${optimalTimesData[0]?.avg_engagement?.toFixed(1)} avg)`
                    : 'Collect more data to get timing recommendations'
                  }
                </p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">📱 Content Strategy</h4>
                <p className="text-blue-700 text-sm">
                  {mediaTypeData.length > 0 
                    ? `${mediaTypeData[0]?.name} performs best with ${mediaTypeData[0]?.avgEngagement?.toFixed(1)} average engagement`
                    : 'Post more content to get strategy recommendations'
                  }
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <h4 className="font-medium text-purple-900 mb-2">📊 Weekly Performance</h4>
                <p className="text-purple-700 text-sm">
                  {weeklyComparison[selectedUsername] ? (
                    weeklyComparison[selectedUsername].changes?.engagement_change_percent >= 0 
                      ? `Great job! Your engagement is up ${weeklyComparison[selectedUsername].changes?.engagement_change_percent?.toFixed(1)}% this week`
                      : `Engagement is down ${Math.abs(weeklyComparison[selectedUsername].changes?.engagement_change_percent)?.toFixed(1)}% - consider trying different content types`
                  ) : (
                    'Need more data to provide weekly performance insights'
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;
