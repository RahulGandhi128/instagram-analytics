import React, { useState, useEffect, useCallback } from 'react';
import { Users, MessageCircle, Heart, TrendingUp, BarChart, Download } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart as RechartsBarChart, Bar } from 'recharts';
import { analyticsAPI } from '../services/api';

const Dashboard = ({ showNotification }) => {
  const [summaryStats, setSummaryStats] = useState(null);
  const [dailyMetrics, setDailyMetrics] = useState([]);
  const [insights, setInsights] = useState({});
  const [selectedUsername, setSelectedUsername] = useState('');
  const [loading, setLoading] = useState(true);
  const [chartTimeRange, setChartTimeRange] = useState(30);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const [summaryRes, metricsRes, insightsRes] = await Promise.all([
        analyticsAPI.getSummaryStats(),
        analyticsAPI.getDailyMetrics({ days: chartTimeRange }),
        analyticsAPI.getInsights({ days: chartTimeRange })
      ]);

      setSummaryStats(summaryRes.data.data);
      setDailyMetrics(metricsRes.data.data);
      setInsights(insightsRes.data.data);
    } catch (error) {
      showNotification('Error loading dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  }, [chartTimeRange, showNotification]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const fetchInstagramData = async () => {
    try {
      showNotification('Fetching latest Instagram data... This may take a few minutes', 'info');
      const response = await fetch('http://localhost:5000/api/fetch-instagram-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      
      if (data.success) {
        showNotification('Instagram data updated successfully!', 'success');
        await fetchDashboardData(); // Refresh dashboard data
      } else {
        showNotification(`Error: ${data.error}`, 'error');
      }
    } catch (error) {
      showNotification('Error fetching Instagram data', 'error');
    }
  };

  const handleUsernameChange = async (username) => {
    setSelectedUsername(username);
    try {
      const [metricsRes, insightsRes] = await Promise.all([
        analyticsAPI.getDailyMetrics({ username, days: chartTimeRange }),
        analyticsAPI.getInsights({ username, days: chartTimeRange })
      ]);
      setDailyMetrics(metricsRes.data.data);
      setInsights(insightsRes.data.data);
    } catch (error) {
      showNotification('Error loading filtered data', 'error');
    }
  };

  const handleTimeRangeChange = async (timeRange) => {
    setChartTimeRange(timeRange);
    try {
      const [metricsRes, insightsRes] = await Promise.all([
        analyticsAPI.getDailyMetrics({ username: selectedUsername, days: timeRange }),
        analyticsAPI.getInsights({ username: selectedUsername, days: timeRange })
      ]);
      setDailyMetrics(metricsRes.data.data);
      setInsights(insightsRes.data.data);
    } catch (error) {
      showNotification('Error loading time range data', 'error');
    }
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

  return (
    <div className="px-4 py-6 sm:px-0">
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
            {usernames.map(username => (
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

      {/* Data Fetching Workflow */}
      <div className="bg-gradient-to-r from-instagram-purple to-instagram-pink rounded-lg p-6 mb-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold mb-2">📱 Instagram Data Workflow</h3>
            <p className="text-sm opacity-90 mb-3">
              Follow these steps: 1️⃣ Fetch latest Instagram data → 2️⃣ View analytics & insights → 3️⃣ Export reports
            </p>
            <p className="text-xs opacity-80">
              * All data synced in IST timezone • Updates profiles, posts, stories & engagement metrics
            </p>
          </div>
          <div className="flex flex-col space-y-2">
            <button
              onClick={fetchInstagramData}
              className="px-6 py-3 bg-white text-instagram-purple font-medium rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 transition-colors"
            >
              🚀 Fetch Latest Data
            </button>
            <p className="text-xs text-center opacity-80">
              ~2-3 minutes
            </p>
          </div>
        </div>
      </div>

      {/* Summary Stats Cards */}
      {summaryStats && (
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
                      Total Profiles
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {summaryStats.total_profiles}
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
                      Total Posts
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {summaryStats.total_posts}
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
                      Active Stories
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {summaryStats.active_stories}
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
                      {summaryStats.recent_posts_week}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Daily Engagement Trend */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Daily Engagement Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dailyMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="total_engagement" 
                stroke="#8884d8" 
                strokeWidth={2}
                name="Total Engagement"
              />
              <Line 
                type="monotone" 
                dataKey="posts_count" 
                stroke="#82ca9d" 
                strokeWidth={2}
                name="Posts Count"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Posts vs Engagement */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Posts vs Engagement</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RechartsBarChart data={dailyMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="posts_count" fill="#8884d8" name="Posts Count" />
              <Bar dataKey="avg_engagement_per_post" fill="#82ca9d" name="Avg Engagement" />
            </RechartsBarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Performance Insights */}
      {currentUserInsights && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Performance Insights - {selectedUsername}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Top Performing Posts */}
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-3">Top 5 Performing Posts</h4>
              <div className="space-y-3">
                {currentUserInsights.top_posts.slice(0, 5).map((post, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex-1">
                      <p className="text-sm text-gray-600">
                        {post.media_type} • {post.engagement} engagement
                      </p>
                      <a 
                        href={post.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-instagram-purple hover:text-instagram-pink text-sm"
                      >
                        View Post
                      </a>
                    </div>
                    <div className="text-right">
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
                {currentUserInsights.bottom_posts.slice(0, 5).map((post, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div className="flex-1">
                      <p className="text-sm text-gray-600">
                        {post.media_type} • {post.engagement} engagement
                      </p>
                      <a 
                        href={post.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-instagram-purple hover:text-instagram-pink text-sm"
                      >
                        View Post
                      </a>
                    </div>
                    <div className="text-right">
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
