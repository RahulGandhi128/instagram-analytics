import React, { useState, useEffect } from 'react';
import { Heart, MessageCircle, Share, Play, ExternalLink, Calendar } from 'lucide-react';
import { analyticsAPI } from '../services/api';
import { useUsernames } from '../hooks/useUsernames';

const MediaPosts = ({ showNotification }) => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    username: '',
    mediaType: '',
    limit: 50
  });
  
  const { usernames } = useUsernames();

  useEffect(() => {
    fetchPosts();
    
    // Listen for global data fetch events
    const handleDataFetched = () => {
      fetchPosts();
    };
    
    window.addEventListener('dataFetched', handleDataFetched);
    
    return () => {
      window.removeEventListener('dataFetched', handleDataFetched);
    };
  }, [filters]);

  const fetchPosts = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.username) params.username = filters.username;
      if (filters.mediaType) params.media_type = filters.mediaType;
      if (filters.limit) params.limit = filters.limit;

      const response = await analyticsAPI.getMedia(params);
      setPosts(response.data.data);
    } catch (error) {
      showNotification('Error loading media posts', 'error');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getMediaTypeColor = (type) => {
    switch (type) {
      case 'reel': return 'bg-red-100 text-red-800';
      case 'carousel': return 'bg-blue-100 text-blue-800';
      case 'post': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-instagram-purple"></div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between mb-6">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Media Posts
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Browse and analyze all Instagram posts
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <select
              value={filters.username}
              onChange={(e) => setFilters({...filters, username: e.target.value})}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value="">All Accounts</option>
              {usernames.map(username => (
                <option key={username} value={username}>{username}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Media Type
            </label>
            <select
              value={filters.mediaType}
              onChange={(e) => setFilters({...filters, mediaType: e.target.value})}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value="">All Types</option>
              <option value="post">Post</option>
              <option value="reel">Reel</option>
              <option value="carousel">Carousel</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Limit
            </label>
            <select
              value={filters.limit}
              onChange={(e) => setFilters({...filters, limit: parseInt(e.target.value)})}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value={25}>25 posts</option>
              <option value={50}>50 posts</option>
              <option value={100}>100 posts</option>
            </select>
          </div>
        </div>
      </div>

      {/* Posts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {posts.map((post) => (
          <div key={post.id} className="bg-white rounded-lg shadow-md overflow-hidden">
            {/* Post Header */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{post.full_name}</h3>
                  <p className="text-sm text-gray-600">@{post.username}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getMediaTypeColor(post.media_type)}`}>
                    {post.media_type}
                  </span>
                  {post.is_video && (
                    <Play className="w-4 h-4 text-gray-500" />
                  )}
                </div>
              </div>
            </div>

            {/* Post Content */}
            <div className="p-4">
              {post.caption && (
                <p className="text-gray-900 mb-3 text-sm leading-relaxed">
                  {post.caption.length > 150 
                    ? `${post.caption.substring(0, 150)}...` 
                    : post.caption
                  }
                </p>
              )}

              {/* Post Metrics */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center text-gray-600">
                    <Heart className="w-4 h-4 mr-1" />
                    <span className="text-sm font-medium">{post.like_count.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <MessageCircle className="w-4 h-4 mr-1" />
                    <span className="text-sm font-medium">{post.comment_count.toLocaleString()}</span>
                  </div>
                  {post.play_count > 0 && (
                    <div className="flex items-center text-gray-600">
                      <Play className="w-4 h-4 mr-1" />
                      <span className="text-sm font-medium">{post.play_count.toLocaleString()}</span>
                    </div>
                  )}
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold text-instagram-purple">
                    {post.engagement_count.toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-500">Total Engagement</div>
                </div>
              </div>

              {/* Post Date and Link */}
              <div className="flex items-center justify-between">
                <div className="flex items-center text-xs text-gray-500">
                  <Calendar className="w-3 h-3 mr-1" />
                  {formatDate(post.post_datetime_ist)}
                </div>
                <a
                  href={post.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-sm text-instagram-purple hover:text-instagram-pink"
                >
                  View Post
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </div>

              {/* Collaboration Info */}
              {post.is_collab && post.collab_with && (
                <div className="mt-2 p-2 bg-blue-50 rounded-md">
                  <div className="text-xs text-blue-700">
                    Collaboration with: {post.collab_with}
                  </div>
                </div>
              )}

              {/* Carousel Info */}
              {post.carousel_media_count > 1 && (
                <div className="mt-2 p-2 bg-gray-50 rounded-md">
                  <div className="text-xs text-gray-600">
                    Carousel with {post.carousel_media_count} items
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Load More */}
      {posts.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500">
            No posts found. Try adjusting your filters.
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaPosts;
