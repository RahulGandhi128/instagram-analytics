import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { BarChart3, Users, TrendingUp, Download, RefreshCw } from 'lucide-react';

// Components
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import MediaPosts from './pages/MediaPosts';
import Profiles from './pages/Profiles';

// Services
import { analyticsAPI } from './services/api';

function App() {
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleFetchData = async () => {
    setLoading(true);
    try {
      await analyticsAPI.fetchData();
      showNotification('Data fetched successfully!', 'success');
    } catch (error) {
      showNotification('Error fetching data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'Analytics', href: '/analytics', icon: TrendingUp },
    { name: 'Media Posts', href: '/media', icon: Users },
    { name: 'Profiles', href: '/profiles', icon: Users },
  ];

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        {/* Navigation */}
        <nav className="bg-white shadow-lg border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-xl font-bold text-instagram-purple">
                    Instagram Analytics
                  </h1>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  {navigation.map((item) => {
                    const Icon = item.icon;
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                      >
                        <Icon className="w-4 h-4 mr-2" />
                        {item.name}
                      </Link>
                    );
                  })}
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={handleFetchData}
                  disabled={loading}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-instagram-purple hover:bg-instagram-pink focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-instagram-purple disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  {loading ? 'Fetching...' : 'Fetch Data'}
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Notification */}
        {notification && (
          <div className={`fixed top-4 right-4 p-4 rounded-md z-50 ${
            notification.type === 'success' ? 'bg-green-100 text-green-700' :
            notification.type === 'error' ? 'bg-red-100 text-red-700' :
            'bg-blue-100 text-blue-700'
          }`}>
            <div className="flex">
              <div className="ml-3">
                <p className="text-sm font-medium">
                  {notification.message}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard showNotification={showNotification} />} />
            <Route path="/analytics" element={<Analytics showNotification={showNotification} />} />
            <Route path="/media" element={<MediaPosts showNotification={showNotification} />} />
            <Route path="/profiles" element={<Profiles showNotification={showNotification} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
